## Code to Work with [Intrinio.com](https://intrinio.com/) API 

Shared code was created in the framework of my research of the US stock market. I've been using it as an `import` in Jupyter Lab and/or Notebook, inasmuch I find these instruments the most comfortable for **research** purposes. But I tried to write a code which won't need complete refactoring on implementation into **production** stage. 
I beleive somebody could find this code usefull to work with [intrinio.com](https://intrinio.com/) API.


### <code>parser</code>
This module is responsible for getting data from the API, also some of the received data is preprocessed (consider `parser.company`). API-key should be provided in `CONFIG_PARSER` dict (which initialized in `technical.config`).</i>

- <code>parser.<b>api</b></code>
Contains `IntrinioAPI` class, which allows to generate html-requests for communication with API. Requests are presented in a raw form as they are presented in [API's documentation](https://docs.intrinio.com/documentation/api_v2/getting_started).

- <code>parser.<b>universe</b></code>Contains `Universe` class, which downloads the list of all available companies and securities (a company may have more then one security) with their descriptions. Obtained data could be used as a companies/securities screener (e.g. to filter out banks and isurance companies) for further research.
     > <i>Initialization will take some time, because it generates pretty large amount of requests to obtain all of the companies' securities, hence I recommend to create a dump of the created `Universe` instance (e.g. using `technical.dumper`).</i>

- <code>parser.<b>company</b></code>
Contains `Company` class, which downloads data for the company, which `company_id` was provided (balance sheet, income and cash flow statements (all of the statements are [standardized](https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2?values=eyJpZCI6IkFBUEwtaW5jb21lX3N0YXRlbWVudC0yMDE4LVExIn0%3D) and [LTM](https://www.investopedia.com/terms/l/ltm.asp)), filing dates, marketcap, main security price, etc.).
     > <i>`MainSecurity` includes data preprocessing algorithms for extracting the 'main' share, other securities (e.g. bonds) are ignored. `FilingDatesClean` filters out periods, for which reporting forms were not provided properly.</i>


### <code>processor</code>

- <code>processor.<b>fieldsCleaner</b></code>
`CollectCleanFields` is the main function of this module. It takes a `Company` class instance and returns `pandas.DataFrame` instance with company's fundamentals. The fundamentals pass several logical tests (the ones, which have not passed the tests, will be filled with `numpy.nan`). Applied logical tests consist of control sums for sections of reporting forms (e.g. 'Total Liabilities' should be equal to sum of 'Current Liabilities' and 'Non-current Liabilities'). 
     > <i>The returned data may be additionally tested (for mistakes) in accordance with further usage purposes (signs ± are incosistent in interest expense, dividends, Sales and probably in some other fields, but mistakes of this kind are rare).</i>

- <code>processor.<b>fundamentals</b></code>
Contains methods for fundamentals extraction and modification - lags and/or stats (mean, median, max, min) for the provided period. Also some 'synthetic' fundamentals are added: Tangible Assets, Book Value, EBIT, EBITDA, FCFF, Financial Debt, Financial Debt Cost,  Net Debt, Part EV (EV minus market capitalization). 


- <code>processor.<b>prices</b></code>
Contains method for extracting market capitalization (missing values are restored from main share price data) and a method, which returns a mapper for matching fundamentals with prices.
     > <i>Main share price (including version adjusted on dividends and splits) could be extracted from `Company` instance (`mainSecurityPrice` attribute).</i>

- processor/<b>RF_FIELDS</b>
Contains 2 files needed for fundamentals extracting and cleaning. `RF_FIELDS.xlsx` file could be used as a reference for existing fundamentals fields.


### <code>technical</code>

- <code>technical.<b>config</b></code>
Contains 2 dicts with parameters for the code.
     > Please, provide your API-key in `CONFIG_PARSER ` dict and path to `processor/RF_FIELDS` in `CONFIG_PROCESSOR` dict. 

- <code>technical.<b>dumper</b></code>
Contains `Dumper` class, which is just a light wrap around [`pickle`](https://docs.python.org/3/library/pickle.html).
