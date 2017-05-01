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

## Example
Here is the financial question that we want to answer: is the Consumer Staples Sector really a defensive sector? How well does it perform when the overall stock market is falling?

To answer this question we will use some data preloaded in *returnsseries* and use the *ReturnsSeries* object to conduct our analysis.
```
import returnsseries.data as rd
rd.spx.tail()
rd.ixr.plot()
```
SPX is the S&P500 Index. IXR is the Consumer Staples sub-sector of the S&P500 Index; this contains companies such as CVS Health and Colgate-Palmolive. 

*rd.spx* is a *pandas.Series* of monthly returns for SPX from Yahoo Finance. *rd.ixr* is a *pandas.Series* of daily returns for IXR from Yahoo Finance. 

The *ReturnsSeries* class handles time-sample conversions, so our analysis can mix data of different frequencies.

We first need to convert our *pandas.Series* objects into *ReturnsSeries*
```
import returnsseries as rs
spx = rs.ReturnsSeries(series=rd.spx, periods_per_year=12)
```
To instantiate a *ReturnsSeries* you need to provide a *pandas.Series* of your return data, and a value for periods_per_year which indicates the frequency of the returns. Because *rd.spx* has monthly returns, we set periods_per_year=12.

In *returnsseries.utils* the function *annual_median* can estimate the number of periods per year from a *pandas.Series* which automates this argument for you. 
```
import returnsseries.utils as ru
periods_per_year = ru.annual_median(rd.ixr)
print periods_per_year
ixr = rs.ReturnsSeries(rd.ixr, periods_per_year)
```

To examine the data, start with the *plot_perf* method. 
```
spx.plot_perf(log2=False)
```
*plot_perf* converts the returns to an account curve (a compounding price-index of the returns) and displays it along with summary statistics. As you can see from this long-term plot of the S&P500, the compounding of returns makes it hard to read a linear plot of the compounding returns. 

If you set *log2=True* the plot will show a base-2 logarithm of the account curve. The tick labels on the y-axis are relabelled to show that the actual account curve is doubling with every unit increase. 
```
spx.plot_perf(log2=True)
```

```
import datetime as dt
obama_years = [(dt.datetime(2009, 1, 20), dt.datetime(2017, 1, 19))]
```