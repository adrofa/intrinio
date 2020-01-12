CONFIG_PARSER = {

    'processes': 10,

    'api_key': '...',  # replace '...' with your API-key

    'timeout_regular': 10,  # timeout (in seconds) for regular requests
    'timeout_bulk': 20,  # timeout (in seconds) for bulk requests

    'retry_regular': 7,  # number of retries in case of unsuccessful API-respond

    'security_coverage_threshold': 0.75,  # for details consider `MainSecurity` method of `Company` class

    'filing_dates': {

        # limits for difference between `filing_date` and `end_date`
        # `end_date` - end of reporting period (e.g. 31-dec-2019)
        # `filing_date` - date of reporting forms publication  (e.g. 01-feb-2020)
        'borders': {'low': 16.476990348666558,  # 14
                    'high': 95.6161313441719},  # 90

        # expected difference between `end_date` of consecutive filings
        'end_interval': {'low': 71,
                         'high': 111,
                         'expected': 91},

        'minimum_years': 3,

        # recreation of start-end (filing dates) intervals
        # for details consider `FilingDatesRaw` method of `Company` class
        'minQ': 14.426817,
        'maxQ': 89.725903,
        'minY': 14.671690,
        'maxY': 89.912859,
    },
}

CONFIG_PROCESSOR = {
    'processes': 10,

    'filing_date_end_threshold': 111,

    'RF_EXCEL_FOLDER': '...',  # provide path to `RF_FIELDS.xlsx` and `RF_TESTS.xlsx` files
    'RF_FIELDS_FILE': 'RF_FIELDS.xlsx',
    'RF_TESTS_FILE': 'RF_TESTS.xlsx'
}
