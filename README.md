## Code to Work with [Intrinio.com](https://intrinio.com/) API 

Shared code was created in the framework of my research of the US stock market. I've been using it as an `import` in Jupyter Notebooks (inasmuch I find this instrument the most comfortable for **research**), but I beleive that the structure of the project will allow to apply it also in **production** (at least, with minor changes).
I hope somebody could find it usefull to work with [intrinio.com](https://intrinio.com/) API.

### <code>parser</code>
<This module is responsible for...>

- <code>parser.<b>api</b></code>
<br/>Shared code provides easy access to Intrinio-API (US stocks), covers fundamental data with logical tets (to filter out mistakes) and restores some missing data. Most of the calculations are vectorized (with `pandas` / `numpy`), which makes feature-generation process rather fast.

- <code>parser.<b>company</b></code>
<br/>Shared code provides easy access to Intrinio-API (US stocks), covers fundamental data with logical tets (to filter out mistakes) and restores some missing data. Most of the calculations are vectorized (with `pandas` / `numpy`), which makes feature-generation process rather fast.

- <code>parser.<b>universe</b></code>
<br/>Shared code provides easy access to Intrinio-API (US stocks), covers fundamental data with logical tets (to filter out mistakes) and restores some missing data. Most of the calculations are vectorized (with `pandas` / `numpy`), which makes feature-generation process rather fast.


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

- <code>processor.<b>technical</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.

- <code>processor.<b>dumper</b></code>
<br/>Less then in 3 hours, I passed through ML project stages (exploratory data analysis, features preparation, model selection, and model tuning), trained a model, which outperforms naive algorithm, found important data insights.
