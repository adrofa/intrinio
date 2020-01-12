import pandas as pd

ROLLING_METHODS = {
    'mean': pd.core.window.Rolling.mean,
    'median': pd.core.window.Rolling.median,

    'max': pd.core.window.Rolling.max,
    'min': pd.core.window.Rolling.min,
}


def FundamentalValue(field, cleanFields, lag=0, periodLen=1, stat='mean'):
    """ Returns pd.Series with fundamental values (for all filing dates) for the provided company.

        --- `field` - field of the reporting form (e.g. `Total Assets`);
        --- `replacer` - if reporting form misses the `field`, `replacer` will be returned,
            if the `replacer` is `None` or `False`, will raise an error;
        --- `lag` - lag for the value to be returned (1 step means 1 year, i.e. 4 quarters), should be ≤0;
        --- `periodLen` - the number of periods to be used for statistic calculation (if any stat applied, e.g. `mean`).
        --- `stat` - statistic to be calculated above the field for the provided period.
    """

    rollingMethod = ROLLING_METHODS[stat]

    quarterIdx = cleanFields.index.to_series()
    quarterIdx = quarterIdx.apply(lambda q: q.split('-')[0])

    colByQ = [cleanFields.loc[quarterIdx[quarterIdx == q].index, field]
              for q in quarterIdx.unique()]

    fv = [col.iloc[::-1].rolling(window=periodLen, min_periods=periodLen) for col in colByQ]
    fv = [rollingMethod(col) for col in fv]
    fv = [col.shift(lag * -1) for col in fv]
    fv = pd.concat(fv)
    fv = fv.loc[quarterIdx.index]

    fundamentalValue = fv.copy()

    return fundamentalValue


def FundamentalValueWithReplacer(field, cleanFields, lag=0, periodLen=1, stat='mean', replacer=0):
    """ Duplicates `FundamentalValue` function. In case `cleanFields` misses the provided field,
    duplicates `Total Assets` column and replaces not null values with the `replacer`.
    """

    if field in cleanFields.columns:
        fundamentalValue = FundamentalValue(field, cleanFields, lag, periodLen, stat)

    else:
        fv = FundamentalValue('Total Assets', cleanFields, lag, periodLen, stat)
        fv.loc[~fv.isnull()] = replacer
        fundamentalValue = fv

    return fundamentalValue


def TangibleAssets(cleanFields, lag=0, periodLen=1, stat='mean'):

    field = 'Total Assets'
    totalAssets = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Goodwill'
    goodwill = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Intangible Assets'
    intangibleAssets = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    tangibleAssets = totalAssets - (goodwill + intangibleAssets)

    return tangibleAssets


def BookValue(cleanFields, lag=0, periodLen=1, stat='mean'):

    tangibleAssets = TangibleAssets(cleanFields, lag, periodLen, stat)

    field = 'Total Liabilities'
    totalLiabilities = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    bookValue = tangibleAssets - totalLiabilities

    return bookValue


def EBIT(cleanFields, lag=0, periodLen=1, stat='mean'):
    """ Feature: `EBIT`. """

    field = 'Consolidated Net Income / (Loss)'
    netIncome = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Interest Expense'
    interestExpense = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Income Tax Expense'
    taxExpense = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    ebit = netIncome - (interestExpense + taxExpense)

    return ebit


def EBITDA(cleanFields, lag=0, periodLen=1, stat='mean'):
    """ Feature: `EBITDA`. """

    ebit = EBIT(cleanFields, lag, periodLen, stat)

    field = 'Depreciation Expense'
    depreciation = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Amortization Expense'
    amortization = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    ebitda = ebit + depreciation + amortization

    return ebitda


def FCFF(cleanFields, lag=0, periodLen=1, stat='mean'):

    field = 'Net Cash From Operating Activities'
    cfo = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Cash Interest Paid'
    interest = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Purchase of Property, Plant & Equipment'
    capex = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    fcff = cfo + interest - capex

    return fcff


def FinancialDebt(cleanFields, lag=0, periodLen=1, stat='mean'):

    field = 'Short-Term Debt'
    stDebt = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Long-Term Debt'
    ltDebt = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Capital Lease Obligations'
    otherDebt = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    financialDebt = stDebt + ltDebt + otherDebt

    return financialDebt


def FinancialDebtCost(cleanFields, lag=0, periodLen=1, stat='mean'):

    financialDebt = FinancialDebt(cleanFields, lag, periodLen, stat)

    field = 'Interest Expense'
    interestExpense = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    financialDebtCost = interestExpense / financialDebt

    return financialDebtCost


def NetDebt(cleanFields, lag=0, periodLen=1, stat='mean'):

    financialDebt = FinancialDebt(cleanFields, lag, periodLen, stat)

    field = 'Cash & Equivalents'
    cashAndEq = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Restricted Cash'
    restrictedCash = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    cash = cashAndEq + restrictedCash

    netDebt = financialDebt - cash

    return netDebt


def PartEV(cleanFields, lag=0, periodLen=1, stat='mean'):

    netDebt = NetDebt(cleanFields, lag, periodLen, stat)

    field = 'Noncontrolling Interest'
    nci = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Redeemable Noncontrolling Interest'
    rnci = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    field = 'Preferred Stock'
    pref = FundamentalValueWithReplacer(field, cleanFields, lag, periodLen, stat, replacer=0)

    partEV = netDebt + nci + rnci + pref

    return partEV


SYNTH_FUNDAMENTALS = {
    'TangibleAssets': TangibleAssets,
    'BookValue': BookValue,
    'EBIT': EBIT,
    'EBITDA': EBITDA,
    'FCFF': FCFF,
    'FinancialDebt': FinancialDebt,
    'FinancialDebtCost': FinancialDebtCost,
    'NetDebt': NetDebt,
    'PartEV': PartEV,
}


def SynthFundamentalValue(synthField, cleanFields, lag=0, periodLen=1, stat='mean', normalize=True):

    function = SYNTH_FUNDAMENTALS[synthField]

    synthFundamentalValue = function(cleanFields, lag, periodLen, stat)

    if normalize:
        normalizer = FundamentalValue('Total Assets', cleanFields, lag=0, periodLen=1, stat='mean')
        synthFundamentalValue = synthFundamentalValue / normalizer

    return synthFundamentalValue


def SynthFundamentalValueChange(synthField, cleanFields, lag=0, periodChange=-2, normalize=True):

    function = SYNTH_FUNDAMENTALS[synthField]

    synthFundamentalValue_T1 = function(cleanFields, lag, periodLen=1, stat='mean')
    synthFundamentalValue_T0 = function(cleanFields, lag+periodChange, periodLen=1, stat='mean')
    change = synthFundamentalValue_T1 - synthFundamentalValue_T0

    if normalize:
        normalizer = FundamentalValue('Total Assets', cleanFields, lag=0, periodLen=1, stat='mean')
        change = change / normalizer

    return change
