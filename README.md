## Code to Work with [Intrinio.com](https://intrinio.com/) API 

Shared code was created in the framework of my research of the US stock market. I've been using it as an `import` in Jupyter Notebook (inasmuch I find this instrument the most comfortable for **research** purposes), but I beleive that the structure of the project will allow to apply it also in **production**, at least after (hopefully) minor modifications.
I beleive somebody could find it usefull to work with [intrinio.com](https://intrinio.com/) API.


### <code>parser</code>
This module is responsible for getting data from the API, also some of the received data is preprocessed (consider `parser.company`). API-key should be provided in `CONFIG_PARSER` dict (which initialized in `technical.config`).</i>

- <code>parser.<b>api</b></code>
<br/>Contains `IntrinioAPI` class, which allows to generate html-requests for communication with API. Requests are presented in a raw form as they are presented in [API's documentation](https://docs.intrinio.com/documentation/api_v2/getting_started).

- <code>parser.<b>universe</b></code>
<br/>Contains `Universe` class, which downloads the list of all available companies and securities (a company may have more then one security) with their descriptions. The obtained data could be used as a companies/securities screener (e.g. to filter out banks and isurance companies) for further research.
<br/><i>
     > Initialization will take some time, because it generates pretty large amount of requests to obtain all of the companies' securities, hence I recommend to create a dump of the obtained data with `technical.dumper`.
</i>

- <code>parser.<b>company</b></code>
<br/>Contains `Company` class, which downloads data for the company, which `company_id` was provided (balance sheet, income and cash flow statements, filing dates, marketcap, main security price, etc.).
<br/><i>
     > I'd highly recommend to study the `MainSecurity` and `FilingDatesClean` methods in more details, because these methods include data preprocessing algorithms for extracting the 'main' stock security (other securities are ignored) and cleaning periods, for which reporting forms were not provided properly.
</i>


### <code>processor</code>

- <code>processor.<b>fieldsCleaner</b></code>
<br/>The notebook presents an algorithm identifying groups of sim-cards, which belongs to one personality. The algorithm is based on geo data from the stations, which transmit mobile signal. By submitting this solution I was offered with a DS position in Megafon.

- <code>processor.<b>fundamentals</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

- <code>processor.<b>prices</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

- processor/<b>RF_FIELDS</b>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

### <code>technical</code>

- <code>technical.<b>config</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

- <code>technical.<b>dumper</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.
