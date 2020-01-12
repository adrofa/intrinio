from ..technical.config import CONFIG_PARSER
from ..parser.api import IntrinioAPI
# --------------------------------------------
import pandas as pd
import numpy as np

import multiprocessing.dummy as multiprocessing
from functools import partial

import datetime
import pytz


class Company(object):

    def __init__(self, company_id, verbose=False):

        startTime = datetime.datetime.now()

        self.company_id = company_id

        self.CF = Company.ReportingFormConsolidated(company_id, 'CF', verbose)
        self.BS = Company.ReportingFormConsolidated(company_id, 'BS', verbose)
        self.IS = Company.ReportingFormConsolidated(company_id, 'IS', verbose)

        self.CF_list = Company.ReportingFormList(company_id, 'CF', verbose)
        self.BS_list = Company.ReportingFormList(company_id, 'BS', verbose)
        self.IS_list = Company.ReportingFormList(company_id, 'IS', verbose)

        self.info = Company.CompanyInfo(company_id, verbose)

        self.securitiesList = Company.SecuritiesList(company_id, verbose)
        security_id_list = self.securitiesList['id'].tolist()
        self.securities = Company.Securities(security_id_list, verbose)

        ms, msi = Company.MainSecurity(self.securities, verbose)
        self.mainSecurity = ms
        self.mainSecurityInfo = msi
        
        if self.mainSecurity is not None:
            self.mainSecurityPrice = Company.Price(self.mainSecurity, verbose)
            self.dividend = Company.Dividend(self.mainSecurity, verbose)

        self.marketcap = Company.MarketCap(company_id, verbose)
        self.sharesOut = Company.SharesOut(company_id, verbose)

        self.initializationDate = datetime.datetime.now(pytz.timezone('US/Eastern'))
        self.updateDate = []
        self.updateInfo = []

        self.filingDates = self.FilingDatesClean()

        endTime = datetime.datetime.now()

        if verbose:
            minutes = round((endTime - startTime).total_seconds() / 60, 2)
            print('{}: initialization completed (in {} minutes)'.format(company_id, minutes))

    @staticmethod
    def CompanyInfo(company_id, verbose=False):
        """ Returns general information about the company. """

        api = IntrinioAPI()

        lc = api.LookupCompany(company_id)
        ci = pd.Series(data=lc, name=company_id)

        dates = [
            'latest_filing_date',
            'first_fundamental_date',
            'last_fundamental_date',
            'first_stock_price_date',
            'last_stock_price_date',
        ]
        for date in dates:
            ci[date] = pd.to_datetime(ci[date])

        if verbose:
            print('{}: CompanyInfo was collected.'.format(company_id))

        return ci

    # Financials
    @staticmethod
    def ReportingFormConsolidated(company_id, form, verbose=False):
        """ Returns pandas.DataFrame, which contain all filings of the provided form
        for the provided ticker.
        """

        lrf = Company.ReportingFormList(company_id=company_id, form=form)

        reporting_form_id_list = lrf['id'].tolist()
        index_list = lrf.index.tolist()

        data = {}
        pool = multiprocessing.Pool(processes=CONFIG_PARSER['processes'])

        api = IntrinioAPI(timeout=60)
        f = partial(Company.ReportingForm, api=api)

        for index, rf in zip(index_list, pool.imap(f, reporting_form_id_list)):
            if rf is not None:
                data[index] = rf
        pool.close()
        pool.join()

        if verbose:
            print('{}: ReportingFormConsolidated - {} was collected.'.format(company_id, form))

        rfc = pd.DataFrame(data).T
        rfc.fillna(0, inplace=True)

        return rfc

    @staticmethod
    def ReportingForm(reporting_form_id, api=None):
        """ Returns reporting form's values (in a Series format). """

        if api is None:
            api = IntrinioAPI()

        sf = api.StandardizedFinancials(reporting_form_id)
        sf = sf['standardized_financials']

        pool = multiprocessing.Pool(processes=CONFIG_PARSER['processes'])
        sfr = pool.map(Company.RestructureRawReportingFormEntry, sf)
        pool.close()
        pool.join()

        rf = pd.DataFrame(sfr)

        if rf.shape != (0, 0):
            rf = pd.Series(data=rf['value'].values, index=rf['name'])
        else:
            rf = None

        return rf

    @staticmethod
    def RestructureRawReportingFormEntry(row):
        """ Restructures Income Statement API response. """

        rowCopy = row.copy()

        value = rowCopy.pop('value')
        rowNew = rowCopy.pop('data_tag')
        rowNew.update({'value': value})

        return rowNew

    @staticmethod
    def ReportingFormList(company_id, form, verbose=False):
        """ Returns a list of existing filings for the provided form for the provided Company
        (in a DataFrame format).
        """

        statement_code = {
            'BS': 'balance_sheet_statement',
            'IS': 'income_statement',
            'CF': 'cash_flow_statement',
        }

        api = IntrinioAPI()

        afbc = api.AllFundamentalsByCompany(
            identifier=company_id,
            statement_code=statement_code[form],
            type='TTM'
        )
        assert afbc['company']['id'] == company_id

        rfl = pd.DataFrame(afbc['fundamentals'])
        rfl.index = rfl['fiscal_period'].str.replace('TTM', '') + '-' + rfl['fiscal_year'].astype('str')

        for date in ['start_date', 'end_date', 'filing_date']:
            rfl[date] = pd.to_datetime(rfl[date])

        rfl.sort_values(by='end_date', ascending=False, inplace=True)

        if verbose:
            print('{}: ReportingFormList - {} was collected.'.format(company_id, form))

        return rfl

    # Securities
    @staticmethod
    def SecuritiesList(company_id, verbose=False):
        """ Returns a list of existing securities for the provided Company (in a DataFrame format). """

        api = IntrinioAPI()

        asbc = api.AllSecuritiesByCompany(company_id)

        asbcSecurities = asbc['securities']
        asbcNextPage = asbc['next_page']

        while asbcNextPage is not None:

            asbcNextPart = api.AllSecuritiesByCompany(company_id, next_page=asbcNextPage)

            asbcSecurities += asbcNextPart['securities']
            asbcNextPage = asbcNextPart['next_page']

        sl = pd.DataFrame(asbcSecurities)

        if verbose:
            print('{}: SecuritiesList was collected.'.format(company_id))

        return sl

    @staticmethod
    def Securities(security_id_list, verbose=False):
        """ Returns the list of all securities with general information about them (in DataFrame format). """

        pool = multiprocessing.Pool(processes=CONFIG_PARSER['processes'])

        si_list = pool.map(Company.SecurityInfo, security_id_list)

        pool.close()
        pool.join()

        securities = pd.concat(si_list, axis=1).T

        if verbose:
            print('Securities were collected.')

        return securities

    @staticmethod
    def SecurityInfo(security_id):
        """ Returns general information about the security. """

        api = IntrinioAPI()

        ls = api.LookupSecurity(security_id)
        si = pd.Series(data=ls, name=security_id)

        dates = [
            'first_stock_price',
            'last_stock_price',
            'last_stock_price_adjustment',
            'last_corporate_action'
        ]

        for date in dates:
            si[date] = pd.to_datetime(si[date])

        return si

    # Main Security
    @staticmethod
    def MainSecurity(securities, verbose=False):
        """ Extracts main security. """

        msc, msci = Company.MainSecurity_conditions(securities)

        sc = Company.SecuritiesCoverage(securities)
        if sc is not None:
            scCount = sc.count() / len(sc)

            if msc is not None:
                coverageShare = scCount[msc]

                if coverageShare >= CONFIG_PARSER['security_coverage_threshold']:
                    ms = msc
                    msci = ' '.join([msci, 'Coverage: {}.'.format(coverageShare)])

                else:
                    ms = None
                    msci = ' '.join([msci, 'Coverage: {}.'.format(coverageShare), 'Coverage criteria is not met.'])

            else:  # msc is None
                coverageAboveThs = scCount[scCount >= CONFIG_PARSER['security_coverage_threshold']]

                if len(coverageAboveThs) == 1:
                    ms = coverageAboveThs.index[0]
                    coverageShare = scCount[ms]
                    msci1 = 'Main security is not detected, but coverage criteria is met only for 1 security.'
                    msci2 = 'Coverage: {}'.format(coverageShare)
                    msci = ' '.join([msci1, msci2])

                else:
                    ms = None
                    msci1 = 'Main security is not detected.'
                    msci2 = 'Coverage criteria is met for {} securities.'.format(len(coverageAboveThs))
                    msci = ' '.join([msci1, msci2])

        else:  # sc is None
            ms = None
            msci = 'Main security is not detected: no stock prices.'

        if verbose:
            print('Main security: {} | Info: {}'.format(str(ms), msci))

        return ms, msci

    @staticmethod
    def MainSecurity_conditions(securities):
        """ Extracts main security_id from securities list. """

        sec = securities[securities['code'] == 'EQS'].copy()
        sec = sec[sec['currency'] == 'USD']

        if len(sec) < 1:
            main_security = None
            main_security_info = 'No `EQS` securities.'
            return main_security, main_security_info

        if len(sec) == 1:
            main_security = sec['id'][0]
            main_security_info = 'One security.'
            return main_security, main_security_info

        if len(sec) > 1:

            prim_sec = sec[sec['primary_security'] == True]
            if len(prim_sec) == 1:
                main_security = prim_sec['id'][0]
                main_security_info = '1 `primary_security` among {} (all) securities.'.format(len(sec))
                return main_security, main_security_info

            prim_lis = sec[sec['primary_listing'] == True]
            if len(prim_lis) == 1:
                main_security = prim_lis['id'][0]
                main_security_info = '1 `primary_listing` among {} (all) securities..'.format(len(sec))
                return main_security, main_security_info

            prim_sec_prim_lis = prim_sec[prim_sec['primary_listing'] == True]
            if len(prim_sec_prim_lis) == 1:
                main_security = prim_sec_prim_lis['id'][0]
                main_security_info = '1 `primary_listing` among {} `primary_security`.'.format(len(prim_sec), len(sec))
                return main_security, main_security_info

            prim_sec_active = prim_sec[prim_sec['active'] == True]
            if len(prim_sec_active) == 1:
                main_security = prim_sec_active['id'][0]
                main_security_info = '1 `active` among {} `primary_security`.'.format(len(prim_sec), len(sec))
                return main_security, main_security_info

            prim_lis_active = prim_lis[prim_lis['active'] == True]
            if len(prim_lis_active) == 1:
                main_security = prim_lis_active['id'][0]
                main_security_info = '1 `active` among {} `primary_listing`.'.format(len(prim_lis))
                return main_security, main_security_info

            prim_act = sec[sec['active'] == True]
            if len(prim_act) == 1:
                main_security = prim_act['id'][0]
                main_security_info = '1 `active` among {} (all) securities.'.format(len(sec))
                return main_security, main_security_info

            main_security = None
            main_security_info = 'Could not detect primary security among {} (all) securities.'.format(len(sec))
            return main_security, main_security_info

    @staticmethod
    def SecuritiesCoverage(securities):
        """ Returns the DataFrame, where:
         - rows are the date range between first and last company's securities price dates;
         - columns - company's securities;
         the cell is filled wih security_id in case the corresponding security was active on the stated date.
        """

        sec = securities[securities['code'] == 'EQS'].copy()
        sec = sec[sec['currency'] == 'USD']

        fspd = sec['first_stock_price'].dropna().min()
        lspd = sec['last_stock_price'].dropna().max()

        if fspd in [np.nan] or lspd in [np.nan]:
            sc = None

        else:
            sc = pd.DataFrame(index=pd.date_range(fspd, lspd))

            security_id_list = sec['id'].tolist()

            for security_id in security_id_list:
                fspd = sec.loc[security_id, 'first_stock_price']
                lspd = sec.loc[security_id, 'last_stock_price']

                if fspd is not None and lspd is not None:

                    sc.loc[fspd:lspd, security_id] = security_id

        return sc

    # Prices
    @staticmethod
    def Price(security_id, verbose=False):
        """" Returns price dynamics for the provided Company (in DataFrame format). """

        api = IntrinioAPI(timeout=CONFIG_PARSER['timeout_bulk'])

        spbs = api.StockPricesBySecurity(security_id, page_size=10000)
        assert spbs['security']['currency'] == 'USD'
        assert spbs['security']['id'] == security_id

        price = pd.DataFrame(spbs['stock_prices'])

        price['date'] = pd.to_datetime(price['date'])
        price.sort_values(by='date', inplace=True, ascending=False)
        price.set_index('date', inplace=True)

        if verbose:
            print('{} (security): price was collected.'.format(security_id))

        return price

    @staticmethod
    def MarketCap(company_id, verbose=False):
        """" Returns marketcap dynamics for the provided Company (in DataFrame format). """

        api = IntrinioAPI(timeout=CONFIG_PARSER['timeout_bulk'])

        hdfc = api.HistoricalDataForCompany(identifier=company_id, tag='marketcap', page_size=10000)

        marketCap = pd.DataFrame(hdfc['historical_data'])

        marketCap['date'] = pd.to_datetime(marketCap['date'])
        marketCap.sort_values(by='date', ascending=False, inplace=True)
        marketCap.set_index('date', inplace=True)
        marketCap.rename(columns={'value': 'marketcap'}, inplace=True)

        if verbose:
            print('{}: marketcap was collected.'.format(company_id))

        return marketCap

    @staticmethod
    def Dividend(security_id, verbose=False):
        """" Returns the DataFrame with the provided security dividend.
        The date (in the returned DataFrame is the `record date` (not the pay date, nor declared date).
        """

        api = IntrinioAPI(timeout=CONFIG_PARSER['timeout_bulk'])

        hdfs = api.HistoricalDataForSecurity(identifier=security_id, tag='dividend', page_size=10000)

        if len(hdfs['historical_data']) != 0:
            dividend = pd.DataFrame(hdfs['historical_data'])

            dividend['date'] = pd.to_datetime(dividend['date'])
            dividend.sort_values(by='date', ascending=False, inplace=True)
            dividend.set_index('date', inplace=True)
            dividend.rename(columns={'value': 'dividend'}, inplace=True)

        else:
            dividend = None

        if verbose:
            print('{} (security): dividend was collected.'.format(security_id))

        return dividend

    @staticmethod
    def SharesOut(company_id, verbose=False):
        """" https://data.intrinio.com/data-tag/weightedavedilutedsharesos """

        api = IntrinioAPI(timeout=CONFIG_PARSER['timeout_bulk'])

        hdfc = api.HistoricalDataForCompany(identifier=company_id, tag='weightedavedilutedsharesos', page_size=10000)

        sharesOut = pd.DataFrame(hdfc['historical_data'])

        sharesOut['date'] = pd.to_datetime(sharesOut['date'])
        sharesOut.sort_values(by='date', ascending=False, inplace=True)
        sharesOut.set_index('date', inplace=True)
        sharesOut.rename(columns={'value': 'sharesOut'}, inplace=True)

        if verbose:
            print('{}: sharesOut was collected.'.format(company_id))

        return sharesOut

    @staticmethod
    def AdjustedClosePrice(company_id, verbose=False):
        """ https://data.intrinio.com/data-tag/adj_close_price """

        api = IntrinioAPI(timeout=CONFIG_PARSER['timeout_bulk'])

        hdfc = api.HistoricalDataForCompany(identifier=company_id, tag='adj_close_price', page_size=10000)

        adjustedClosePrice = pd.DataFrame(hdfc['historical_data'])

        adjustedClosePrice['date'] = pd.to_datetime(adjustedClosePrice['date'])
        adjustedClosePrice.sort_values(by='date', ascending=False, inplace=True)
        adjustedClosePrice.set_index('date', inplace=True)
        adjustedClosePrice.rename(columns={'value': 'adjustedClosePrice'}, inplace=True)

        if verbose:
            print('{}: adjustedClosePrice was collected.'.format(company_id))

        return adjustedClosePrice

    # Filing Dates
    def FilingDatesClean(self):
        """ From restored filing dates:
        -- leaves only filing dates for which all of RFs are available;
        -- removes tail with missed (Q- / Y-) filings;
        returns pd.DataFrame with cleared filing dates.
        """

        fd = self.FilingDatesRaw()

        idxBS = set(self.BS.index)
        idxIS = set(self.IS.index)
        idxCF = set(self.CF.index)

        idxALL = idxBS.intersection(idxIS, idxCF)
        idxALL = [idx for idx in idxALL if idx in fd.index]

        assertionText = '{}: No intersecting periods between `ReportingForms`.'.format(self.company_id)
        assert len(idxALL) > 0, assertionText

        fd = fd.loc[idxALL, :].sort_values(by='end_date', ascending=False).copy()

        config = CONFIG_PARSER['filing_dates'].copy()
        low = config['end_interval']['low']
        high = config['end_interval']['high']
        expected = config['end_interval']['expected']

        fd['diff'] = (fd['end_date'].shift(1) - fd['end_date']).dt.days
        assertionText = '{}: More then 1 missing dates diff.'.format(self.company_id)
        assert fd['diff'].isnull().sum() == 1, assertionText
        fd['diff'] = fd['diff'].fillna(expected)

        while not fd['diff'].between(low, high).all():
            rowsToSave = fd[fd['diff'].between(low, high)].index.tolist()
            fd = fd.loc[rowsToSave, :]

            fd['diff'] = (fd['end_date'].shift(1) - fd['end_date']).dt.days
            fd['diff'] = fd['diff'].fillna(expected)

        fdClean = fd.drop(columns='diff')

        return fdClean

    def FilingDatesRaw(self):
        """ Restores filing dates from available RF_FIELDS, returns pd.DataFrame with them.

        Output may include filings for which there are no RF_FIELDS on the Server.
        This will happen for filings for which API returns empty list of values.
        """

        rflBS = self.BS_list.copy()
        rflBS['filing_date'] = rflBS['filing_date'].dt.tz_localize(None)
        rflBS['delay'] = (rflBS['filing_date'] - rflBS['end_date']).dt.total_seconds() / (60 * 60 * 24)

        cols = ['end_date', 'filing_date', 'delay']
        rowsQ = rflBS[rflBS['fiscal_period'] != 'FY'].index
        rowsY = rflBS[rflBS['fiscal_period'] == 'FY'].index

        # Quarters
        fdQ = rflBS.loc[rowsQ, cols].copy()

        fdSeries = fdQ['filing_date']
        edSeries = fdQ['end_date']
        fdQ['filing_date'] = [Company.ExtractFilingDate(end_date, fdSeries) for end_date in edSeries]
        fdQ['delay'] = (fdQ['filing_date'] - fdQ['end_date']).dt.total_seconds() / (60 * 60 * 24)

        minQ = fdQ['delay'].min()
        if np.isnan(minQ):
            minQ = CONFIG_PARSER['filing_dates']['borders']['low']
        maxQ = fdQ['delay'].max()
        if np.isnan(maxQ):
            minQ = CONFIG_PARSER['filing_dates']['borders']['high']

        fdQ['filing_date_start'] = fdQ['filing_date'].copy()
        fdQ['filing_date_end'] = fdQ['filing_date'].copy()

        # FYs
        fdY = rflBS.loc[rowsY, cols].copy()

        fdSeries = fdY['filing_date']
        edSeries = fdY['end_date']
        fdY['filing_date'] = [Company.ExtractFilingDate(end_date, fdSeries) for end_date in edSeries]
        fdY['delay'] = (fdY['filing_date'] - fdY['end_date']).dt.total_seconds() / (60 * 60 * 24)

        minY = fdY['delay'].min()
        if np.isnan(minY):
            minY = CONFIG_PARSER['filing_dates']['borders']['low']
        maxY = fdY['delay'].max()
        if np.isnan(maxY):
            maxY = CONFIG_PARSER['filing_dates']['borders']['high']

        fdY['filing_date_start'] = fdY['filing_date'].copy()
        fdY['filing_date_end'] = fdY['filing_date'].copy()

        # Whole table
        colsToCopy = ['end_date', 'filing_date', 'filing_date_start', 'filing_date_end']

        fd = pd.concat([fdQ.loc[fdQ.index, colsToCopy].copy(), fdY.loc[fdY.index, colsToCopy].copy()])
        fd.sort_values(by='end_date', ascending=False, inplace=True)

        fd.loc[rowsQ, 'period'] = 'Q'
        fd.loc[rowsY, 'period'] = 'Y'

        # - Filling NaNs
        rowsNan = fd[fd['filing_date'].isnull()].index
        rowsNanQ = (fd['filing_date'].isnull()) & (fd['period'] == 'Q')
        rowsNanY = (fd['filing_date'].isnull()) & (fd['period'] == 'Y')

        fd.loc[rowsNan, 'end_date'] = rflBS.loc[rowsNan, 'end_date'].copy()

        fd.loc[rowsNanQ, 'filing_date_start'] = fd.loc[rowsNanQ, 'end_date'] + pd.to_timedelta(minQ, 'days')
        fd.loc[rowsNanQ, 'filing_date_end'] = fd.loc[rowsNanQ, 'end_date'] + pd.to_timedelta(maxQ, 'days')

        fd.loc[rowsNanY, 'filing_date_start'] = fd.loc[rowsNanY, 'end_date'] + pd.to_timedelta(minY, 'days')
        fd.loc[rowsNanY, 'filing_date_end'] = fd.loc[rowsNanY, 'end_date'] + pd.to_timedelta(maxY, 'days')

        fd.sort_values(by='end_date', ascending=False, inplace=True)

        # Assertions
        company_id = self.company_id
        config = CONFIG_PARSER['filing_dates'].copy()

        assertionText = '{}: filing_date_start is before end_date'.format(company_id)
        assert (fd['end_date'] < fd['filing_date_start']).all(), assertionText

        assertionText = '{}: filing_date_end is before filing_date_start'.format(company_id)
        assert (fd['filing_date_start'] <= fd['filing_date_end']).all(), assertionText

        val = config['borders']['high']
        assertionText = '{}: At least one filing_date_end is {} or more days after end_date.'.format(company_id, val)
        assert ((fd['filing_date_end'] - fd['end_date']).dt.days < val).all(), assertionText

        val = config['borders']['high'] - config['borders']['low']
        assertionText = \
            '{}: difference between filing_date_start and filing_date_end is {} days or more'.format(company_id, val)
        valsToCheck = (fd['filing_date_end'] - fd['filing_date_start']).dt.total_seconds() / (60 * 60 * 24)
        assert (valsToCheck < val).all(), assertionText

        return fd

    @staticmethod
    def ExtractFilingDate(end_date, filing_date_series):
        """ Returns filing date from the provided list if any, otherwise returns NaN. """

        low = CONFIG_PARSER['filing_dates']['borders']['low']
        high = CONFIG_PARSER['filing_dates']['borders']['high']

        diff = (filing_date_series - end_date).dt.total_seconds() / (60 * 60 * 24)
        diffBounded = diff[(low <= diff) & (diff <= high)]

        if len(diffBounded) > 0:
            idx = diffBounded.idxmin()
            fd = filing_date_series[idx]
        else:
            fd = pd.to_datetime(np.nan)

        return fd


class DummyCompany(object):

    def __init__(self):
        pass
