## Code to Work with [Intrinio.com](https://intrinio.com/) API 

Shared code was created in the framework of my research of the US stock market. I've been using it as an `import` in Jupyter Notebook (inasmuch I find this instrument the most comfortable for **research** purposes), but I beleive that the structure of the project will allow to apply it also in **production**, at least after (hopefully) minor changes applied.
I beleive somebody could find it usefull to work with [intrinio.com](https://intrinio.com/) API.

### <code>parser</code>
This module is responsible for getting data from the API, also some of received data is preprocessed (consider `parser.company`).<br/>
> <i>To receive data API-key should be provided in `CONFIG_PARSER` dict (which initialized in `technical.config`).</i>

- <code>parser.<b>api</b></code>
Contains `IntrinioAPI` class, which allows to generate html-requests for communication with API. Requests are ppresented in a raw form as they are presented in [API's documentation](https://docs.intrinio.com/documentation/api_v2/getting_started).

- <code>parser.<b>universe</b></code>
Contains `Universe` class 

- <code>parser.<b>company</b></code>
Contai




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
