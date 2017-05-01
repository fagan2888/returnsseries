# [![Brooksbridge](logo/brooksbridge_logo.jpg)](https://github.com/smithto1/returnsseries.git) [returnsseries](https://github.com/smithto1/returnsseries.git)

*returnsseries* defines the ReturnSeries object, a new subclass of the pandas.Series that is designed specifically for handling financial returns which brings powerful plotting and analysis capabilities. 

## Install *returnsseries*
### pip install
```
pip install git+https://github.com/smithto1/returnsseries.git
```
### Install from source
Clone the repository from GitHub
```
git clone https://github.com/smithto1/returnsseries.git
```
Then in the parent directory of *returnsseries* run
```
python setup.py install
```

## Prerequisites
### Python
*returnsseries* is written for Python 2
### Package Dependencies
* numpy
* pandas
* matplotlib

## Authors
* [**Thomas Smith**](https://www.linkedin.com/in/thomassmithcfa/)

## License
*returnsseries* is licensed under the GNU General Public License v3. A copy of which is included in LICENSE

## Example
Here is the financial question that we want to answer: is the Consumer Staples Sector really a defensive sector? How well does it perform when the overall stock market is falling?

To answer this question we will use some data preloaded in *returnsseries* and use the *ReturnsSeries* object to conduct our analysis.
```
import returnsseries.data as rd
rd.spx.tail()
```

```
Date
2016-12-31    0.018201
2017-01-31    0.017884
2017-02-28    0.037198
2017-03-31   -0.000389
2017-04-30    0.009091
Freq: M, Name: SPX, dtype: float64
```

SPX is the S&P500 Index. IXR is the Consumer Staples sub-sector of the S&P500 Index; this contains companies like CVS Health and Colgate-Palmolive. 

*rd.spx* is a *pandas.Series* of monthly returns for SPX from Yahoo Finance. *rd.ixr* is a *pandas.Series* of daily returns for IXR from Yahoo Finance. 

The *ReturnsSeries* class handles time-sample conversions, so our analysis can mix data of different frequencies.

We first need to convert our *pandas.Series* objects into *ReturnsSeries*.
```
import returnsseries as rs
spx = rs.ReturnsSeries(series=rd.spx, periods_per_year=12)
```
To instantiate a *ReturnsSeries* you need to provide a *pandas.Series* of your return data, and a value for *periods_per_year* which indicates the frequency of the returns. Because *rd.spx* has monthly returns, we set *periods_per_year=12*.

In *returnsseries.utils* the function *annual_median* can estimate the number of periods per year from a *pandas.Series* which automates this argument for you. 
```
import returnsseries.utils as ru
periods_per_year = ru.annual_median(rd.ixr)
ixr = rs.ReturnsSeries(rd.ixr, periods_per_year)
```

To examine the data, start with the *plot_perf* method. 
```
spx.plot_perf(log2=False)
```
![plot0](logo/plot0.png "spx.plot_perf(log2=False)")

*plot_perf* converts the returns to an account curve (a compounding price-index of the returns) and displays it along with summary statistics. As you can see from this long-term plot of the S&P500, the compounding of returns makes it hard to read a linear plot of compounding returns. 

If you set *log2=True* the plot will show a base-2 logarithm of the account curve. The tick labels on the y-axis are relabelled to show that the actual account curve is doubling with every unit increase. 
```
spx.plot_perf(log2=True)
```
![plot1](logo/plot1.png "spx.plot_perf(log2=True)")

On plots we often want to focus on certain time periods, so it should be easy to highlight them. To show how easily this can be done, let's highlight how the S&P500 did while Steve Jobs was CEO of Apple Computer. 
```
import datetime as dt
steve_jobs_is_ceo = [(dt.datetime(1976, 4, 1), dt.datetime(1985, 9, 16)),
                     (dt.datetime(1997, 9, 16), dt.datetime(2011, 8, 24)),]
spx.plot_perf(log2=True, shade_dates=steve_jobs_is_ceo)
```
![plot2](logo/plot2.png "spx.plot_perf(log2=True, shade_dates=steve_jobs_is_ceo)")

Putting highlights on plots is cool, but we want them to be informative. Like any smart investor you are probably thinking about your risk, and what happens to your investments in a bear market.

The *ReturnsSeries* makes it easy to examine bear markets. 
```
spx_bear_dates = spx.bear_periods(limit=-.20)
print spx_bear_dates
spx.plot_perf(log2=True, shade_dates=spx_bear_dates)
```
```
(Timestamp('1962-01-31 00:00:00'), Timestamp('1962-06-30 00:00:00', freq='M'))
(Timestamp('1968-12-31 00:00:00'), Timestamp('1970-06-30 00:00:00', freq='M'))
(Timestamp('1973-01-31 00:00:00'), Timestamp('1974-09-30 00:00:00', freq='M'))
(Timestamp('1980-12-31 00:00:00'), Timestamp('1982-07-31 00:00:00', freq='M'))
(Timestamp('1987-09-30 00:00:00'), Timestamp('1987-11-30 00:00:00', freq='M'))
(Timestamp('2000-09-30 00:00:00'), Timestamp('2002-09-30 00:00:00', freq='M'))
(Timestamp('2007-11-30 00:00:00'), Timestamp('2009-02-28 00:00:00', freq='M'))
```
![plot3](logo/plot3.png "spx.plot_perf(log2=True, shade_dates=spx_bear_dates)")

The *bear_periods* method will return the start and end dates of any peak-to-trough drawdown that exceeds the *limit* arg. These start and end dates can then be passed into the *shade_dates* arg of the *plot_perf*. 

Using the standard definition that a bear market is a peak-to-trough fall of 20% or more, we can see that the S&P500 had bear markets starting in 1962, 1968, 1973, 1980, 1987, 2000 and 2007.

We can also use these same dates to highlight performance across other assets. On *returnsseries.plot* the function *plot_perf* has the same features but can plot a list of *ReturnsSeries* objects. 
```
import returnsseries.plot as rp
spx = spx[ixr.index.min():]
rp.plot_perf([spx, ixr], log2=True, shade_dates=spx_bear_dates)
```
![plot4](logo/plot4.png "rp.plot_perf([spx, ixr], log2=True, shade_dates=spx_bear_dates)")

Because IXR only starts in 1998 we will cut down our SPX data so we only look at them over their overlapping time periods. Here we can see that when the S&P500 was in a bear market the Consumer Staples sector was also down, although it appears that it fell by less. 

Interestingly, over their entire overlapping sample periods IXR and and SPX had almost exactly the same return statistics, both at 4.3% average annual return. 

Looking at the plots is helpful, we can generally see what is happeing. But for a sophisticated investor like you, you want hard numbers. What did this defensive sector actually return in a bear market?

```
import pandas as pd

spx_bear_summaries = spx.period_returns_summaries(spx_bear_dates, within=True)
pd.concat(spx_bear_summaries, axis=1)

ixr_bear_summaries = ixr.period_returns_summaries(spx_bear_dates, within=True)
pd.concat(ixr_bear_summaries, axis=1)
```
Using the *period_returns* and *period_returns_summaries* methods we can create and summarise *ReturnsSeries* objects for any subperiod of our data. Using the *spx_bear_dates* we can see the total returns for both SPX and IXR during in the periods when the S&P 500 was in a bear market. 

It seems that while SPX lost -46% and -52% in the bear markets of 2000 and 2007, IXR lost -20% and -29%. So it seems that over these time periods, Consumer Staples somewhat defensive, but not miraculously defensive: it outperformed the overall index, but still suffered significant losses. 
```
                         2000-09-30  2007-11-30
Cumulative Return (%)         -46.3       -52.6
Annual Return (%)             -26.7         -45
Annual Volatility (%)          17.7        19.6
Sharpe Ratio                  -1.51       -2.29
Worst Drawdown (%)              -43         -50
Worst Drawdown Date      2002-09-30  2009-02-28
Time to Recover (Mths)          NaN         NaN
Longest Drawdown (Mths)          24          15
Longest Drawdown End     2002-09-30  2009-02-28
Start Date               2000-09-30  2007-11-30
End Date                 2002-09-30  2009-02-28
Track Record (Yrs)                2         1.2


                         2000-09-30  2007-11-30
Cumulative Return (%)         -20.7       -29.8
Annual Return (%)               -11       -24.7
Annual Volatility (%)          17.9        26.1
Sharpe Ratio                  -0.62       -0.95
Worst Drawdown (%)              -34         -31
Worst Drawdown Date      2002-07-19  2009-02-27
Time to Recover (Mths)          NaN         NaN
Longest Drawdown (Mths)          21          15
Longest Drawdown End     2002-09-30  2009-02-27
Start Date               2000-10-02  2007-11-30
End Date                 2002-09-30  2009-02-27
Track Record (Yrs)                2         1.2
```

That tells us about individual periods, but what if we want a more commplete summary: how does each index do in bear markets vs bull markets?
```
names = ['All Data', 'SPX Bear Prds', 'SPX Bull Prds']
spx_combined_summary = spx.periods_combined_summary(periods=spx_bear_dates, names=names)
pd.concat(spx_combined_summary, axis=1)

ixr_combined_summary = ixr.periods_combined_summary(periods=spx_bear_dates, names=names)
pd.concat(ixr_combined_summary, axis=1)
```
For this we use the *periods_combined_summary* method. This method returns 3 summaries:
1. A summary of all the data in the *ReturnsSeries*
2. A summary of the data that lies **inside** the subperiods defined by the *perods* arg
3. A summary of the data that lies **outside** the subperiods defined by the *periods* arg

Since the subperiods defined by *spx_bear_dates* are the SPX bear markets, I rename the columns *['All Data', 'SPX Bear Prds', 'SPX Bull Prds']*.

```
                       All Data  SPX Bear Prds  SPX Bull Prds
Cumulative Return (%)    117.00         -74.50         751.50
Annual Return (%)          4.30         -33.70          15.30
Annual Volatility (%)     14.70          18.60          12.10
Sharpe Ratio               0.29          -1.81           1.27
Track Record (Yrs)        18.40           3.30          15.00


                       All Data  SPX Bear Prds  SPX Bull Prds
Cumulative Return (%)    116.10         -44.30         288.10
Annual Return (%)          4.30         -16.50           9.30
Annual Volatility (%)     15.20          21.40          13.50
Sharpe Ratio               0.28          -0.77           0.69
Track Record (Yrs)        18.50           3.20          15.30
```
This allows us to see how each index perfomed in different market environments. Looking down the first column, which summarises all of the data, we can see that SPX and IXR had very similar performance overall. Cumulative Return, Volatility and Sharpe Ratio are all near identical. 

However, if we look across the rows they do look different. The SPX performed quite differently across Bear and Bull periods, with respective Sharpe Ratios of -1.81 and 1.27. The IXR is much more balanced across environments, with Bear and Bull Sharpe Ratios of -0.77 and 0.69. 

This analysis suggest that the Consumer Staples sector has been an effective, but not miraculous, defensive investment for the last 20 years. When the overall market index was in its worst bear markets, Consumer Staples also declined but declined a lot less. 