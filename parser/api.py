from ..technical.config import CONFIG_PARSER
# --------------------------------------------
import requests
from retry import retry

defaultApiKey = CONFIG_PARSER['api_key']
defaultRetryNum = CONFIG_PARSER['retry_regular']
defaultTimeout = CONFIG_PARSER['timeout_regular']


class IntrinioAPI(object):

    def __init__(self, apiKey=defaultApiKey, retryNum=defaultRetryNum, timeout=defaultTimeout):
        self.apiKey = apiKey
        self.retryNum = retryNum
        self.timeout = timeout

    # Companies
    def AllCompanies(self, **params):
        """ Returns all Companies. When parameters are specified, returns matching companies.
        https://docs.intrinio.com/documentation/web_api/get_all_companies_v2
        """

        url = 'https://api-v2.intrinio.com/companies'
        acom = IntrinioAPI.RequestJson(self, url, **params)

        return acom

    def LookupCompany(self, identifier):
        """ Returns the Company with the given `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_company_v2
        """

        url = 'https://api-v2.intrinio.com/companies/{identifier}'.format(identifier=identifier)
        lc = IntrinioAPI.RequestJson(self, url)

        return lc

    def AllSecuritiesByCompany(self, identifier, **params):
        """ Returns Securities for the Company with the given `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_company_securities_v2
        """

        url = 'https://api-v2.intrinio.com/companies/{identifier}/securities'.format(identifier=identifier)
        asbc = IntrinioAPI.RequestJson(self, url, **params)

        return asbc

    def AllFundamentalsByCompany(self, identifier, **params):
        """ Returns all Fundamentals for the Company with the given `identifier`.
        Returns Fundamentals matching parameters when supplied.
        """

        url = 'https://api-v2.intrinio.com/companies/{identifier}/fundamentals'.format(identifier=identifier)
        afbc = IntrinioAPI.RequestJson(self, url, **params)

        return afbc

    def HistoricalDataForCompany(self, identifier, tag, **params):
        """ Returns historical values for the given `tag` and the Company with the given `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_company_historical_data_v2
        """

        url = 'https://api-v2.intrinio.com/companies/{identifier}/historical_data/{tag}'
        url = url.format(identifier=identifier, tag=tag)
        hdfc = IntrinioAPI.RequestJson(self, url, **params)

        return hdfc

    # Securities
    def AllSecurities(self, **params):
        """ Returns all Securities to which you have access. When parameters are specified, returns matching Securities.
        https://docs.intrinio.com/documentation/web_api/get_all_securities_v2
        """

        url = 'https://api-v2.intrinio.com/securities'
        asec = IntrinioAPI.RequestJson(self, url, **params)

        return asec

    def LookupSecurity(self, identifier):
        """ Returns the Security with the given `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_security_by_id_v2
        """

        url = 'https://api-v2.intrinio.com/securities/{identifier}'.format(identifier=identifier)
        ls = IntrinioAPI.RequestJson(self, url)

        return ls

    def StockPricesBySecurity(self, identifier, **params):
        """ Return end-of-day stock prices for the Security with the given `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_security_stock_prices_v2
        """

        url = 'https://api-v2.intrinio.com/securities/{identifier}/prices'.format(identifier=identifier)
        sf = IntrinioAPI.RequestJson(self, url, **params)

        return sf

    def HistoricalDataForSecurity(self, identifier, tag, **params):
        """ Returns historical values for the given `tag` and the Security with the given `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_security_historical_data_v2
        """

        url = 'https://api-v2.intrinio.com/securities/{identifier}/historical_data/{tag}'
        url = url.format(identifier=identifier, tag=tag)
        hdfs = IntrinioAPI.RequestJson(self, url, **params)

        return hdfs

    # Stock Exchanges
    def AllStockExchanges(self, **params):
        """ Returns all Stock Exchanges matching the specified parameters.
        https://docs.intrinio.com/documentation/web_api/get_all_stock_exchanges_v2
        """

        url = 'https://api-v2.intrinio.com/stock_exchanges'
        ase = IntrinioAPI.RequestJson(self, url, **params)

        return ase

    def SecuritiesByExchange(self, identifier, **params):
        """ Returns Securities traded on the Stock Exchange with `identifier`.
        https://docs.intrinio.com/documentation/web_api/get_stock_exchange_securities_v2
        """

        url = 'https://api-v2.intrinio.com/stock_exchanges/{identifier}/securities'.format(identifier=identifier)
        sbe = IntrinioAPI.RequestJson(self, url, **params)

        return sbe

    # Fundamentals
    def StandardizedFinancials(self, identifier):
        """ Returns standardized filing, requested with given `identifier`. """

        url = 'https://api-v2.intrinio.com/fundamentals/{identifier}/standardized_financials'
        url = url.format(identifier=identifier)
        sf = IntrinioAPI.RequestJson(self, url)

        return sf

    # Technical
    def RequestJson(self, url, **params):

        @retry(tries=self.retryNum, delay=self.timeout)
        def RequestWithOutRetry():

            params.update({'api_key': self.apiKey})

            r = requests.get(url, params)
            d = r.json()

            if 'error' in d:
                # print('=' * 120)
                # print('REQUEST:', r.url)
                # print('-' * 120)
                # print('RESPONSE:', d)
                # print('=' * 120)
                raise Exception('`error` in API response.')
            else:
                return d

        return RequestWithOutRetry()
