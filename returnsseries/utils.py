"""Utility funcs that underlie methods for ReturnsSeries class"""
import numpy as np
import pandas as pd

def annual_median(srs):
    """Estimate the periods_per_year/freqency of a pandas.Series
    
    Note
    ----
    Estimates the frequency/periodicity/periods_per_year of a pandas.Series. 
    First resamples the series to an annual frequency and counts all of the 
    non-NaN values per year. Years with a count of zero are discluded. First 
    and last year are discluded, as they are likely to be partial years. 
    Median across all remaining years is returned. 
    
    Parameters
    ----------
    srs: pandas.Series
        pandas.Series with index of timestamps
    
    Returns
    -------
    int
        median number of non-NaN values across each year that has data, 
        discluding the first and last calendar years as they are likely to be 
        partial years. """
    rtn = srs.resample('A', 'count')
    rtn = rtn.replace(0, np.nan).dropna()
    rtn = rtn[1:-1].median()
    return rtn


def drawdown_days(drawdowns):
    """A rolling count of the length of each drawdown in days. 
    
    Parameters
    ----------
    drawdowns: pandas.Series
        A timestamped series of drawdown values (percentage losses since 
        previous peak)
    
    Returns
    -------
    pandas.Series
        index is the same as drawdowns arg, values are a rolling count of 
        the number of days the returns are in drawdown from previous peak. 
    """
    days = [0]
    for i in range(1, drawdowns.shape[0]):
        if drawdowns[i]==0:
            cum_days = 0
        else:
            new_days = (drawdowns.index[i] - drawdowns.index[(i-1)]).days
            cum_days = days[-1] + new_days
        days.append(cum_days)
    
    days = pd.Series(days, drawdowns.index)
    
    return days


def date_of_worst(drawdowns):
    """Return the most recent index value of worst drawdown. 
    
    Parameters
    ----------
    drawdowns: pandas.Series
        A timestamped series of drawdown values (percentage losses since 
        previous peak)
    
    Returns
    -------
    pandas.tslib.Timestamp
        Most recent timestamp/index value where drawdowns arg is at its 
        worst drawdown/minimum. 
    """
    mask = drawdowns == drawdowns.min()
    rtn = drawdowns[mask].index[-1]
    return rtn


def days_to_recover(drawdowns, start_date):
    """Number of days to recover from drawdown following specified start date.
    
    Parameters
    ----------
    drawdowns: pandas.Series
        A timestamped series of drawdown values (percentage losses since 
        previous peak)
    start_date: datetime.datetime
        A date that falls within the range of the drawdowns.index that defines
        the start of the reovery period. 
    
    Returns
    -------
    pandas.tslib.Timedelta
        Number of days after start_date that it takes drawdowns arg to 
        recover to previous peak."""
    recovered_date = recovery_date(drawdowns, start_date)
    rtn = recovered_date - start_date
    return rtn


def recovery_date(drawdowns, start_date):
    """Timestamp/index value where drawdowns recover to previous peak.
    
    Parameters
    ----------
    drawdowns: pandas.Series
        A timestamped series of drawdown values (percentage losses since 
        previous peak)
    start_date: datetime.datetime
        A date that falls within the range of the drawdowns.index that defines
        the start of the reovery period. 
    
    Returns
    -------
    pandas.tslib.Timestamp
        Timestampe/index value where drawdowns recover to previous peak."""
    dd_cut = drawdowns[start_date:]
    recovered = dd_cut == 0
    recovered = dd_cut[recovered]
    rtn = recovered.index.min()
    return rtn


def account_curve(returns):
    """Convert returns into a cumulative, compounding price-index.
        
    Parameters
    ----------
    returns: pandas.Series
        pandas.Series of returns/percentage changes
    
    Returns
    -------
    pandas.Series
        index is the same as returns arg, values are the cumulative, 
        compounding price-index of the returns. (returns + 1).cumprod()"""
    return (returns + 1).cumprod()


def drawdowns(account_curve):
    """Rolling percentage decline from previous peak.
    
    Note
    ----
    Drawdown value of zero means account_curve is at peak.
        
    Parameters
    ----------
    account_curve: pandas.Series
        values are a cumulative, compounded price-index
    
    Returns
    -------
    pandas.Series
        index is the same as account_curve arg, values are percentage decline
        from the account_curve's previous peak.""" 
    rolling_max = pd.rolling_max(account_curve, window=account_curve.shape[0], 
                                 min_periods=1)
    drawdowns_ts = account_curve/rolling_max - 1
    drawdowns_ts.name = account_curve.name
    
    return drawdowns_ts


def streak_index(bools, first_row_starts_streak=False):
    """Find the start and end index values for every streak of True values.
            
    Parameters
    ----------
    bools: pandas.Series
        pandas.Series where all values are type bool, True/False
    
    Returns
    -------
    list
        list of tuples, each tuple is of lenght 2, each tuple contains two 
        entries from index of bools arg. First entry indicates the start of a 
        streak of True bools. Second entry indicates the end of a streak of 
        True bools."""       
    binary = pd.Series(0, bools.index)
    binary[bools] = 1
    diffs = binary.diff()
    
    diffs.iloc[0] = 0
    if first_row_starts_streak:
        if bools[0]:
            diffs.iloc[0] = 1.
        else:
            diffs.iloc[0] = 0.

    starts = bools[diffs == 1].index    
    ends = diffs.shift(-1)
    ends = bools[ends == -1].index
    
    if len(starts) > len(ends):
        ends = ends.append(bools.index[-1:])
    
    rtn = zip(starts, ends)
    
    return rtn


def trough_dates(drawdowns, limit=0.):
    """Return index values for peak-to-trough drawdowns that exceed limit.
    
        
    Parameters
    ----------
    drawdowns: pandas.Series
        A timestamped series of drawdown values (percentage losses since 
        previous peak).
    limit: float, optional, default 0.
        Only return the start and end dates of a peak-to-trough drawdown if it 
        is less than limit arg. limit arg should be a non-positive value. 
    
    Returns
    -------
    list
        list of tuples, each tuple is of length 2, each tuple contains 2 values
        from the index of the drawdowns arg. The two entries are the start 
        date and end date of a peak-to-trough drawdown that is <= limit arg"""    
    bools = drawdowns < 0
    dates = streak_index(bools)
    
    rtn = []
    for start, end in dates:
        cut = drawdowns[start:end]
        min_ = cut.min()
        if min_ <= limit:
            min_date = cut[cut == cut.min()].index[-1]
            pair = (start, min_date)
            rtn.append(pair)
    
    return rtn


def within_dates(srs, dates, outside_value):
    """Return series keeping only that values that fall within subperiods.
    
        
    Parameters
    ----------
    srs: pandas.Series
    dates: list
        list of tuples, each tuple contains 2 entries, both entries are used 
        to slice a subsection of the srs arg. First entry defines the start of 
        a subperiod. Second entry defines the end of a subperiod.
    outside_value: 
        The value to assign to all values that fall outside of the subperiods 
        defined by dates arg. outside_value could be almost anything but 
        usually it will be numpy.nan.
    
    Returns
    -------
    pandas.Series
        Returns a copy of srs arg, but all of the values that have an index 
        that does not fall within a subperiod defined by dates arg will be 
        overwrittend with outside_value arg.
    """
    within_limits = []
    for start, end in dates:
        within_limits.extend(srs[start:end].index)
    outside_limits = set(srs.index).difference(set(within_limits))
    rtn = srs.copy()
    rtn[outside_limits] = outside_value
    return rtn


def diff(x, periods=1, ffill_subtrahend=False):
    """Calculate the difference along axis=0 with forward filling subtrahend.
    
    Note
    ----
    difference = minuend - subtrahend
        
    Parameters
    ----------
    x: pandas.Series, pandas.DataFrame
    periods: int, optional, default 1
        Periods to shift for forming difference
    ffill_subtrahed: bool, default False
        Use infinite forward filling of subtrahend to calculate differences
    
    Returns
    -------
    pandas.Series, pandas.DataFrame
        Returns same type as srs arg. Values are now differences between 
        values. With ffill_subtrahend=True differnces in each row will be 
        between current row and last non-NaN value."""
    if ffill_subtrahend:
        subtrahend = x.ffill(limit=None, axis=0).shift(periods)
    else:
        subtrahend = x.shift(periods)
    rtn = x - subtrahend
    
    return rtn


def in_range(index, range_, within):
    """Return bools specifying if index values are inside/outside range_.
        
    Parameters
    ----------
    index: list
        An array-type of values to be used as the index of a pandas.Series
    range_: list
        An array-type with a min value and max value that define a range 
        within the index arg
    within: bool
        If True, return True for all the index values that are inside the 
        range_ arg. If False, return True for all the index values that are 
        outside the range_ arg.
        
    Returns
    -------
    pandas.Series
        index is the index arg, values are True/False specifying if index 
        values are inside/outside the range_ arg"""
    rtn = pd.Series(False, index)
    rtn[ min(range_) : max(range_) ] = True
    if not within:
        rtn = np.invert(rtn)
    return rtn


def in_ranges(index, ranges, within):
    """Return bools specifying if index values are inside/outside the ranges.
        
    Parameters
    ----------
    index: list
        An array-type of values to be used as the index of a pandas.Series
    ranges: list
        A list of array-types; each array-type has a min value and max value 
        that define a range within the index arg
    within: bool
        If True, return True for the index values that fall inside any one of 
        the ranges. If False, return True for the index values that fall 
        outside all of the ranges.
        
    Returns
    -------
    pandas.Series
        index is the index arg, values are True/False specifying if index 
        values are inside/outside the ranges arg"""
    srsl = [in_range(index, range_, within) for range_ in ranges]
    rtn = pd.concat(srsl, axis=1)
    if within:
        rtn = rtn.any(axis=1)
    else:
        rtn = rtn.all(axis=1)
    return rtn


def keep_ranges(df, ranges, within):
    """Keep only the values where index falls inside/outside ranges
        
    Parameters
    ----------
    df: pandas.Series, pandas.DataFrame
    ranges: list
        A list of array-types; each array-type has a min value and max value 
        that define a range within the index arg
    within: bool
        If True, keep the values where index falls within one of ranges. If 
        False, keep the values where index falls outside all of the ranges.
        
    Returns
    -------
    pandas.Series, pandas.DataFrame
        index matches df.index, values will be set to numpy.nan if their index 
        values fall outside/inside ranges."""
    bools = in_ranges(df.index, ranges, within)
    bools = np.invert(bools)
    rtn = df.copy()
    rtn[bools] = np.nan
    return rtn


def dropna_and_reindex(df, **kwargs):
    """"Drop NaNs and reindex so it finishes at df.index[-1]
    
    Note
    ----
    The index that on the returned object is mostly meaningless. All of the 
    non-NaN values are preserved but their Timestamps/index values are changed 
    so the index cannot reliably be used in calculations.
    
    Parameters
    ----------
    df: pandas.Series, pandas.DataFrame
    kwargs: keywords
        keyword args to pass to df.dropna
    
    Returns
    -------
    pandas.Series, pandas.DataFrame
        values are all of the non-NaN values from df arg, index values are all 
        contained within df.index but they no longer align within their 
        original values."""
    rtn = df.copy()
    rtn = rtn.dropna(**kwargs)
    index_use = df.index[-rtn.shape[0]:]
    rtn.index = index_use
    return rtn
