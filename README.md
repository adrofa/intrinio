## Code to Work with [Intrinio.com](https://intrinio.com/) API 

Shared code was created in the framework of my research of the US stock market. I've been using it as an `import` in Jupyter Lab and/or Notebook (inasmuch I find these instruments the most comfortable for **research** purposes), but I beleive that the structure of the project will allow to apply it also in **production**, at least after (hopefully) minor modifications.
I beleive somebody could find this code usefull to work with [intrinio.com](https://intrinio.com/) API.


### <code>parser</code>
This module is responsible for getting data from the API, also some of the received data is preprocessed (consider `parser.company`). API-key should be provided in `CONFIG_PARSER` dict (which initialized in `technical.config`).</i>

- <code>parser.<b>api</b></code>
<br/>Contains `IntrinioAPI` class, which allows to generate html-requests for communication with API. Requests are presented in a raw form as they are presented in [API's documentation](https://docs.intrinio.com/documentation/api_v2/getting_started).

- <code>parser.<b>universe</b></code>
<br/>Contains `Universe` class, which downloads the list of all available companies and securities (a company may have more then one security) with their descriptions. Obtained data could be used as a companies/securities screener (e.g. to filter out banks and isurance companies) for further research.
<br/><i>
     > Initialization will take some time, because it generates pretty large amount of requests to obtain all of the companies' securities, hence I recommend to create a dump of the created `Universe` instance (e.g. using `technical.dumper`).
</i>

- <code>parser.<b>company</b></code>
<br/>Contains `Company` class, which downloads data for the company, which `company_id` was provided (balance sheet, income and cash flow statements (all of the statements are [standardized](https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2?values=eyJpZCI6IkFBUEwtaW5jb21lX3N0YXRlbWVudC0yMDE4LVExIn0%3D) and [LTM](https://www.investopedia.com/terms/l/ltm.asp)), filing dates, marketcap, main security price, etc.).
<br/><i>
     > `MainSecurity` includes data preprocessing algorithms for extracting the 'main' share, other securities (e.g. bonds) are ignored. `FilingDatesClean` filters out periods, for which reporting forms were not provided properly.
</i>


### <code>processor</code>

- <code>processor.<b>fieldsCleaner</b></code>
`CollectCleanFields` is the main function of this module. It takes a `Company` class instance and returns `pandas.DataFrame` instance with company's fundamentals. The fundamentals passes several logical tests (the ones, which have not passed the tests, will be filled with `numpy.nan`). Applied logical tests consists of control sums for sections of reporting forms (e.g. 'Total Liabilities' should be equal to sum of 'Current Liabilities' and 'Non-current Liabilities'). 
     > <i>The returned data should be additionally tested (for mistakes) in accordance with further usage purposes.</i>

- <code>processor.<b>fundamentals</b></code>


- <code>processor.<b>prices</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

- processor/<b>RF_FIELDS</b>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

### <code>technical</code>

- <code>technical.<b>config</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

- <code>technical.<b>dumper</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.
