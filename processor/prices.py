import pandas as pd
import numpy as np


def ExtractPeriodMapper(company):
    """ Returns pd.DataFrame, which maps reporting form period to the price date
    according to filing date/period (not to the end of reporting period!).
    """

    # inputs
    price = company.mainSecurityPrice.copy()
    fd = company.filingDates.copy()

    # start
    priceIndexMin = price.index.min()
    fdEndMin = fd['filing_date_end'].min().normalize()
    start = max(priceIndexMin, fdEndMin)

    # end
    priceIndexMax = price.index.max()
    fdEndMaxAdj = fd['filing_date_end'].max() + pd.to_timedelta(91, 'days')
    fdEndMaxAdj = fdEndMaxAdj.normalize()
    end = min(priceIndexMax, fdEndMaxAdj)

    # `price` clean
    price = price[price.index.to_series().between(start, end)].copy()

    # `filingDates` enriched
    fd['date'] = fd['filing_date_end'].dt.normalize()
    fd['period_full'] = fd.index
    fd['fds'] = fd['filing_date_start'].dt.normalize()
    fd['fde'] = fd['filing_date_end'].dt.normalize()
    fd['diff'] = (fd['fde'] - fd['fds']).dt.total_seconds() / 60 / 60 / 24

    # `periodMapper` initialized
    periodMapper = pd.DataFrame()
    periodMapper['date'] = price.index

    # `periodMapper` enriched
    periodMapper = periodMapper.merge(fd[['date', 'period_full']], how='left', on='date')
    periodMapper = periodMapper.set_index('date')
    periodMapper['period_full'] = periodMapper['period_full'].fillna(method='ffill')

    # collecting list of filing dates
    fdList = fd[fd['diff'] == 0]['fde'].to_list()

    fdPeriodsStart = fd[fd['diff'] != 0]['fds']
    fdPeriodsEnd = fd[fd['diff'] != 0]['fde']

    for start, end in zip(fdPeriodsStart, fdPeriodsEnd):
        fdListUpdate = pd.date_range(start, end, freq='D').to_list()
        fdListUpdate = [date.normalize() for date in fdListUpdate]

        fdList += fdListUpdate

    fdList = [date for date in fdList if date in periodMapper.index]
    fdList.sort()

    # filling filing dates mapper with NaNs
    periodMapper.loc[fdList, :] = np.nan
    periodMapper = periodMapper.dropna()

    return periodMapper


def ExtractMarketcap(company):
    """ Restores marketcap from available data for the provided company
    basing on available prices.
    """

    marketcap = company.marketcap.copy()
    price = company.mainSecurityPrice.copy()
    periodMapper = ExtractPeriodMapper(company)

    marketcapSynth = periodMapper.merge(marketcap, how='left', left_index=True, right_index=True)
    marketcapSynth = marketcapSynth.merge(price[['adj_close']], how='left', left_index=True, right_index=True)

    marketcapSynth['sharesOut_synth'] = marketcapSynth['marketcap'] / marketcapSynth['adj_close']
    marketcapSynth['sharesOut_synth'] = marketcapSynth['sharesOut_synth'].fillna(method='ffill')

    marketcapSynth['marketcap_synth'] = marketcapSynth['adj_close'] * marketcapSynth['sharesOut_synth']

    marketcap = marketcapSynth['marketcap_synth'].rename('marketcap').to_frame()

    return marketcap
