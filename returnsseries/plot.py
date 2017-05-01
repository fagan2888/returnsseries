"""Plotting funcs for ReturnsSeries class"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import returnsseries.utils as ru
import returnsseries.displayfunctions as rd

def plot_perf(returns_list, log2, shade_dates=None, shade_color='lightblue', 
              yticks_round=1, legend_loc='lower right', 
              summary_funcs=rd.summaries['ts'], **kwargs):
    """Plot a list of ReturnsSeries with relevant summary stats

    Parameters
    ----------
    returns_list: list
        list of ReturnsSeries
    log2: bool
        Passed to ReturnsSeries.account_curve. If False result will be 
        price-index of compounding returns. If True result will be base-2 
        logarithm (numpy.log2) of price-index and will reset the y-axis 
        label and y-axis tick labels to reflect the log scale
    shade_dates: list, optional, default None
        List of tuples, each tuple of length 2, each tuple contains start 
        date and end date of time periods to shade with color
    shade_color: str, optional, default 'lightblue'
        String specifying the color to use for shade_dates. Accepts any 
        valid matplotlib color name/string
    yticks_round: int, optional, default 1
        Number of decimals the y-axis tick lables should be rounded to
    legend_loc: str, optional, default 'lower right'
        Specifies where to place pyplot.legend, accepts any string that is 
        valid for pyplot.legend loc arg
    summary_funcs: list, optional, 
    default returnsseries.displayfunctions.summaries['ts']
            list of functions passed into ReturnsSeries.summary
    kwargs: keywords
        Any keyword arguments to pass to matplotlib.pyplot.plot
    
    Returns
    -------
    None"""

    for rtns in returns_list:
        rtns.plot_line(log2, shade_dates, **kwargs)
    
    if log2:
        yticks_log2(yticks_round)
    
    summary_df = pd.concat([rtns.summary(summary_funcs) \
                            for rtns in returns_list], axis=1)
    text_topleft(summary_df)
    
    if legend_loc is not None:
        plt.legend(loc=legend_loc)
    
    return None


def correl_calc(returns_list, base_series):
    """Calculate correlation between all series in returns_list and base_series

    Parameters
    ----------
    returns_list: list
        list of pandas.Series
    base_series: int
        Specifies which entry in returns_list to calculate the 
        correlation with. must have 0 <= base_series < len(returns_list)
        
    Returns
    -------
    pandas.Series
        index are the pandas.Series.name from the entries in returns_list,
        values are the correlations between each series and the seriers in 
        returns_list[base_series]
    """      
    correlations = pd.concat(returns_list, axis=1).corr()
    correlations = correlations.iloc[:,base_series]
    correlations = correlations.round(2)
    name = correlations.index[base_series]
    correlations.name = "Correlation with {}".format(name)    
    return correlations


def shade_dates(shade_dates, srs, color):
    """Color in area below srs between index values in shade_dates
    
    Note
    ----
    Operates on active plotting figure.
    
    Parameters
    ----------
    shade_dates: list
        list of tuples, each tuple contains 2 entries, entries define the 
        start and end of a subperiod within srs.index to be shaded in
    srs: pandas.Series
        values define the y-values to color beneath
    color: str
        Name of the color to use, can be any valid matplotlib color name
    
    Returns
    -------
    None"""   
    maxs = ru.within_dates(srs, shade_dates, np.nan)
    
    mins = maxs.copy()
    ylim_min = min(plt.ylim())
    mins[ np.invert(mins.isnull()) ] = ylim_min
    
    plt.fill_between(mins.index, mins.values, maxs.values, color=color)
    
    return None

def yticks_log2(round_=1):
    """Relabel y-axis for log2 plot
    
    Note
    ----
    Operates on active plotting figure.
    
    Parameters
    ----------
    round_: int, optional, default 1
        Number of digits to round y-axis tick labels to, passed to numpy.round
    
    Returns
    -------
    None"""
    y_tick_locs, y_tick_labels = plt.yticks()
    new_labels = np.round(pow(2, y_tick_locs), round_)
    plt.yticks(y_tick_locs, new_labels)
    plt.ylabel('Logarithmic Return Scale')
    return None


def text_topleft(str_):
    """Write a text in the top-left corner of active plotting figure
    
    Parameters
    ----------
    str_: str
        Text string to write
    
    Returns
    -------
    None"""
    xlims = plt.xlim()
    xdiff = max(xlims) - min(xlims)
    text_x = min(xlims) + xdiff * .01
    text_y = max(plt.ylim()) * .99
    plt.text(text_x, text_y, str_, horizontalalignment='left',
            verticalalignment='top', family='monospace')
    return None
