from ..technical.config import CONFIG_PROCESSOR
# --------------------------------------------
import pandas as pd
import numpy as np
import os


RF_EXCEL_FOLDER = CONFIG_PROCESSOR['RF_EXCEL_FOLDER']
RF_FIELDS_FILE = CONFIG_PROCESSOR['RF_FIELDS_FILE']
RF_TESTS_FILE = CONFIG_PROCESSOR['RF_TESTS_FILE']

RF_FIELDS = pd.read_excel(os.path.join(RF_EXCEL_FOLDER, RF_FIELDS_FILE))
FIELDS_BY_MAIN_RF = {RF: RF_FIELDS[RF_FIELDS['main_RF'] == RF]['field'].unique()
                     for RF in RF_FIELDS['main_RF'].unique()}

RF_TESTS = pd.read_excel(os.path.join(RF_EXCEL_FOLDER, RF_TESTS_FILE))
activeTests = RF_TESTS[RF_TESTS['Value'] == 'on']['Test'].unique()
RF_TESTS = RF_TESTS[RF_TESTS['Test'].isin(activeTests)]


def CollectCleanFields(company):
    """ Returns DataFrame with fields from all of 3 forms. """

    RFname_list = FIELDS_BY_MAIN_RF.keys()

    cleanFields = [ProcessRF(company, RFname) for RFname in RFname_list]
    cleanFields = pd.concat(cleanFields, axis=1)

    return cleanFields


def ProcessRF(company, RFname):
    """ Returns RF with cleaned rows:
    - only rows from filing dates left;
    - rows with errors filled with NaNs.
    """

    errorRows = CollectErrorsDf(company).any(axis=1)
    fdi = errorRows.index

    RF = ExtractReportingForm(company, RFname)

    fields = FIELDS_BY_MAIN_RF[RFname]
    fields = [field for field in fields if field in RF.columns]

    RFclean = RF.loc[fdi, fields]
    RFclean.loc[errorRows, :] = np.nan

    return RFclean


def CollectErrorsDf(company):
    """ Returns df with results of active RF tests.
    CLEAN ROWS LEFT (cleaned by filing dates)!
    """

    fdi = company.filingDates.index.copy()
    normalizer = company.BS.loc[fdi, 'Total Assets'].copy()

    errorsDf = pd.DataFrame(index=fdi)

    for RFname in ['BS', 'IS', 'CF']:

        RF = ExtractReportingForm(company, RFname)
        RF = RF.loc[fdi, :]

        testDf = RF_TESTS[RF_TESTS['RF'] == RFname].copy()
        testDict = {testName: testDf[testDf['Test'] == testName].copy() for
                    testName in testDf['Test'].unique() if
                    testName != 'no_test'}

        for testName in testDict:

            test = testDict[testName]

            # noinspection PyBroadException
            try:
                result = ApplyTestRF(RF, test, normalizer, threshold=0.03)
            except:
                result = True

            errorsDf[testName] = result

    return errorsDf


def ApplyTestRF(RF, test, normalizer, threshold=0.03):
    """ Checks if all totals collected properly (look at `BS_VALIDATION_DICT` for more details).
    Returns df, where 1 means `error` and 0 means `ok`.
    """

    AssertTest(test)

    controlSum = test.loc[test['Value'] == 'on', 'Field'].values[0]
    controlSumCols_dict = {field: value for field, value in zip(test['Field'], test['Value'])
                           if field in RF.columns and value != 'on'}

    for col in controlSumCols_dict:
        RF[col] = RF[col] * controlSumCols_dict[col]

    RF['diff'] = RF[controlSum] - RF[controlSumCols_dict.keys()].sum(axis=1)
    RF['diff_normed'] = RF['diff'] / normalizer
    RF['diff_normed_abs'] = RF['diff_normed'].abs()

    test = (RF['diff_normed_abs'] > threshold)
    zero = (RF[list(controlSumCols_dict.keys()) + [controlSum]] == 0).all(axis=1)

    resultsDF = pd.DataFrame()
    resultsDF['test'] = test
    resultsDF['zero'] = zero

    result = resultsDF.any(axis=1)

    return result


def AssertTest(test):
    """ Checks if provided `test` doesn't contain errors. """

    assertionText = 'ControlSum test - more then 1 `RF`.'
    assert test['RF'].nunique() == 1, assertionText

    assertionText = 'ControlSum test - more then 1 `controlSum`.'
    controlSum = test.loc[test['Value'] == 'on', 'Field'].values[0]
    assert type(controlSum) == str, assertionText


def ExtractReportingForm(company, RFname):
    """ SHOULD BE BASED ON COLLECTED COLS. """
    """ Returns provided RF. """

    if RFname == 'BS':
        RF = company.BS.copy()
    elif RFname == 'IS':
        RF = company.IS.copy()
    elif RFname == 'CF':
        RF = company.CF.copy()
    else:
        exceptionText = '{}: Wrong reporting form (should be: `BS`, `IS`, `CF`.'
        exceptionText = exceptionText.format(RFname)
        raise Exception(exceptionText)

    return RF
