from ..technical.config import CONFIG_PARSER
from ..parser.api import IntrinioAPI
from ..parser.company import Company
# --------------------------------------------
import pandas as pd
import multiprocessing.dummy as multiprocessing
from tqdm import tqdm


class Universe(object):

    def __init__(self):

        self.companiesList = Universe.CompaniesList()
        self.company_id_list = self.companiesList['id'].tolist()
        self.companies = Universe.Companies(self.company_id_list)

        self.securitiesList = Universe.SecuritiesList(self.company_id_list)
        self.security_id_list = self.securitiesList['id'].tolist()
        self.securities = Universe.Securities(self.security_id_list)

    @staticmethod
    def CompaniesList():
        """ Returns all companies DataFrame. """

        params = {
            'has_fundamentals': 'True',
            'has_stock_prices': 'True',
            'page_size': '10000'
        }

        api = IntrinioAPI(timeout=CONFIG_PARSER['timeout_bulk'])

        acom = api.AllCompanies(**params)

        acomCompanies = acom['companies']
        acomNextPage = acom['next_page']

        while acomNextPage is not None:

            params['next_page'] = acomNextPage

            acomNextPart = api.AllCompanies(**params)

            acomCompanies += acomNextPart['companies']
            acomNextPage = acomNextPart['next_page']

        companiesList = pd.DataFrame(acomCompanies)

        return companiesList

    @staticmethod
    def Companies(company_id_list):
        """ Returns all companies DataFrame. """

        pool = multiprocessing.Pool(processes=CONFIG_PARSER['processes'])

        ci_list = []
        for ci in tqdm(pool.imap(Company.CompanyInfo, company_id_list), total=len(company_id_list)):
            ci_list.append(ci)

        pool.close()
        pool.join()

        companies = pd.concat(ci_list, axis=1).T

        return companies

    @staticmethod
    def SecuritiesList(company_id_list):
        """ Returns all securities DataFrame. """

        pool = multiprocessing.Pool(processes=CONFIG_PARSER['processes'])

        sl_list = []
        for sl in tqdm(pool.imap(Company.SecuritiesList, company_id_list), total=len(company_id_list)):
            sl_list.append(sl)

        pool.close()
        pool.join()

        securitiesList = pd.concat(sl_list)

        return securitiesList

    @staticmethod
    def Securities(security_id_list):
        """ Returns the list of all securities with general information about them (in DataFrame format). """

        pool = multiprocessing.Pool(processes=CONFIG_PARSER['processes'])

        si_list = []
        for si in tqdm(pool.imap(Company.SecurityInfo, security_id_list), total=len(security_id_list)):
            si_list.append(si)

        pool.close()
        pool.join()

        securities = pd.concat(si_list, axis=1).T

        return securities
