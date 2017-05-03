"""Subclass of pandas.Series designed specifically for financial returns."""
import numpy as np
import pandas as pd
import warnings as wa
import datetime as dt
import pandas.stats.moments as mo
import matplotlib.pyplot as plt 

import returnsseries.plot as rp
import returnsseries.utils as ru
import returnsseries.displayfunctions as rd

class ReturnsSeries(pd.core.series.Series):
    def __init__(self, series, periods_per_year):
        """Subclass of pandas.Series specifically designed for financial returns
        
        Note
        ----
        For an automated function to calculate periods_per_year of a 
        pandas.Series see returnsseries.utils.annual_median function.
        
        Parameters
        ----------
        series: pandas.Series
            A pandas.Series that has an index of timestamps and values that 
            are financial returns (percentage changes between timestamps).
        periods_per_year: int
            Integer that specifies the frequency of the data in terms of 
            periods per year. For monthly returns, periods_per_year=12. For 
            weekly returns periods_per_year=52."""
        pd.core.series.Series.__init__(self, data=series.values, 
                                       index=series.index, name=series.name,
                                       dtype=series.dtype.type)
        
        self.__periods_per_year__ = periods_per_year
        
        return None
    
    @property
    def periods_per_year(self):
        """int,float: The frequency of the returns data stated in terms of 
        periods per year (i.e. for monthly returns self.periods_per_year=12, 
        for weekly returns self.periods_per_year=52)"""
        return self.__periods_per_year__
    
    def __repr__(self):
        """Return a string representation of the object."""
        rtn = super(ReturnsSeries, self).__repr__()
        rtn = rtn + "\nperiods_per_year: " + str(self.periods_per_year)
        return rtn
    
    def __to_returnsseries__(self, srs):
        """Try to convert a pandas.Series to a ReturnsSeries.
        
        Note
        ----
        The ReturnsSeries that is returned will have the same 
        self.periods_per_year as the ReturnsSeries instance that the method 
        is called from.
        
        Parameters
        ----------
        srs : pandas.Series
            A pandas.Series to try to convert to a ReturnsSeries
        
        Returns
        -------
        ReturnsSeries, pandas.Series
            If the converstion is successful a ReturnsSeries is returned. But
            if trying the conversion raises a a TypeError or AttributeError 
            the same pandas.Series that was passed in will be returned."""
        try:
            rtn = ReturnsSeries(srs, self.periods_per_year)
        except (TypeError, AttributeError):
            rtn = srs  
        return rtn
    
    def __getitem__(self, key):
        """Call pandas.Series parent method and return as a ReturnsSeries."""
        srs_res = super(ReturnsSeries, self).__getitem__(key)
        rtn = self.__to_returnsseries__(srs_res) 
        return rtn
    
    def mul(self, *args, **kwargs):
        """Call pandas.Series parent method and return as a ReturnsSeries."""
        srs_res = super(ReturnsSeries, self).mul(*args, **kwargs)
        rtn = self.__to_returnsseries__(srs_res)
        return rtn
    
    def div(self, *args, **kwargs):
        """Call pandas.Series parent method and return as a ReturnsSeries."""
        srs_res = super(ReturnsSeries, self).div(*args, **kwargs)
        rtn = self.__to_returnsseries__(srs_res)
        return rtn
    
    def copy(self, deep=True):
        """Call pandas.Series parent method and return as a ReturnsSeries."""
        srs_res = super(ReturnsSeries, self).copy(deep)
        rtn = self.__to_returnsseries__(srs_res)
        return rtn
    
    def shift(self, periods=1, freq=None, axis=0, **kwds):
        """Call pandas.Series parent method and return as a ReturnsSeries."""
        srs_res = super(ReturnsSeries, self).shift(periods, freq, axis, **kwds)
        rtn = ReturnsSeries(srs_res, self.periods_per_year)
        return rtn
    
    def replace(self, *args, **kwargs):
        """Call pandas.Series parent method and return as a ReturnsSeries."""
        srs_res = super(ReturnsSeries, self).replace(*args, **kwargs)
        return self.__to_returnsseries__(srs_res)
    
    def account_curve(self, log2=False):
        """Create a price-index by compounding up the returns. 
        
        Note
        ----
        Effectively (ReturnsSeries + 1).cumprod(). Uses the 
        returnsseries.utils.account_curve function.
        
        Parameters
        ----------
        log2: bool, optional, default False
            If False result will be a price-index of the compounded returns 
            beginning at 1. If True result wil be base-2 logarithm of the 
            price-index (numpy.log2()) beginning at zero.
        
        Returns
        -------
        pandas.Series
            index is the same as the ReturnsSeries, values are the price-index 
            from compounding up the returns.
        """
        rtn = ru.account_curve(self)
        if log2:
            rtn = np.log2(rtn)
        return rtn
    
    def drawdowns(self):
        """Return a pandas.Series of percentage fall from previous peak.
        
        Note
        ----
        Uses the returnsseries.utils.drawdowns function. 
        
        Returns
        -------
        pandas.Series
            index is the same as the ReturnsSeries, values are the percentage 
            fall from the previous peak. The maximum value in the returned 
            values will always be 0.0; this means the values acheived a new 
            peak at that timestamp."""
        return ru.drawdowns(self.account_curve())
    
    def bear_periods(self, limit):
        """Return start and end of peak-to-trough drawdowns that exceed limit.
        
        Parameters
        ----------
        limit: float
            The drawdown level that defines a 'bear market', should be a 
            negative number.
        
        Returns
        -------
        list
            The result is a list of tuples, each tuple has length of 2 and 
            contains 2 values from the ReturnsSeries.index that define the 
            start and end of the bear period."""
        return ru.trough_dates(self.drawdowns(), limit)
    
    def track_record_days(self):
        """Return time-difference between start/end of index in days."""
        days = (self.index.max() - self.index.min()).days
        return days
    
    def track_record_length(self, quote_fraction_of_year=1.):
        """Return time-difference between start/end of index in any units.
        
        Parameters
        ----------
        quote_fraction_of_year: float, optional, default 1.
            The time period to quote the results in, specified as a fraction 
            of a year. For result in monthly terms quote_fraction_of_year=1/12.
            For result in weekly terms quote_fraction_of_year=1/52.
        
        Returns
        -------
        float
            The length of the track record (time difference between start of
            index and end of index) in the units determined by 
            quote_fraction_of_year.  Default unit is years."""
        days_per_prd = 365.25 * quote_fraction_of_year
        rtn = self.track_record_days() / days_per_prd
        return rtn
    
    def cum_return(self):
        """Cumulative return of the entire series of returns."""
        acct_curve = self.account_curve()
        first_value = 1.
        last_value = acct_curve[-1]
        rtn = last_value / first_value - 1
        return rtn
    
    def average_return(self, quote_fraction_of_year=1., 
                       upsample_partial_periods=False):
        """Cumulative return expressed as a per-period average return. 
        
        Note
        ----
        Certain financial reporting rules (GIPS - Global Investment 
        Performance Standards) do not allow you to annualise returns if you 
        have less tha 1 year of data; you can only express it as the total 
        cumulative return. To control for this use upsample_partial_periods
        parameter. 
        
        Parameters
        ----------
        quote_fraction_of_year: float, optional, default 1.
            The time period to quote the results in, specified as a fraction 
            of a year. For result in monthly terms quote_fraction_of_year=1/12.
            For result in weekly terms quote_fraction_of_year=1/52.
        upsample_partial_periods: bool, optional, default False
            If the time period covered by the ReturnsSeries is shorter than 
            the time period to average over (as specified by 
            quote_fraction_of_year) use the shorter of the two time periods. 
            If you only have 6 months of data and you request the annual 
            average return with upsample_partial_periods=False, it will 
            return the cumulative return for the whole 6 months but will not 
            annualise it. 
        
        Returns
        -------
        float
            The total cumulative return of all the data expressed as a 
            per-period average compounding return for the time period 
            specified by quote_fraction_of_year. Defaults to annual average
            return."""
        if not upsample_partial_periods:
            num_prds = self.track_record_length(quote_fraction_of_year)
            quote_fraction_of_year = min([quote_fraction_of_year, 
                                          num_prds])
        
        quote_days = 365.25 * quote_fraction_of_year
        num_periods = self.track_record_days() / quote_days
        
        total_return = self.cum_return()
        total_gross_return = total_return + 1
        
        rtn = pow(total_gross_return, 1./num_periods) - 1
        
        return rtn
    
    def vol(self, quote_fraction_of_year=1.):
        """Standard deviation of all returns.
        
        Parameters
        ----------
        quote_fraction_of_year: float, optional, default 1.
            The time period to quote the results in, specified as a fraction 
            of a year. For result in monthly terms quote_fraction_of_year=1/12.
            For result in weekly terms quote_fraction_of_year=1/52.
        
        Returns
        -------
        float
            The volatility/standard deviaton for the entire sample of returns
            quoted for a specified time-period length. Default time period is
            1 year (annual volatiliy)."""
        quote_periods = float(quote_fraction_of_year) * self.periods_per_year
        rtn = self.std() * np.sqrt(quote_periods)
        
        return rtn
    
    def ewmvol(self, quote_fraction_of_year=1., **kwargs):
        """Calculate rolling volatility.
        
        Note
        ----
        Uses pandas.stats.moments.ewmvol function.
        
        Parameters
        ----------
        quote_fraction_of_year: float, optional, default 1.
            The time period to quote the results in, specified as a fraction 
            of a year. For result in monthly terms quote_fraction_of_year=1/12.
            For result in weekly terms quote_fraction_of_year=1/52.
        kwargs: keywords
            Keyword arguments to pass to pandas.stats.moments.ewmvol
        
        Returns
        -------
        pandas.Series
            index is the same as the ReturnsSeries, values are the rolling 
            volatility of returns quoted in terms of the time period specified 
            by quote_fraction_of_year. Default quote_fraction_of_year=1. 
            returns annualised volatility."""
        quote_periods = float(quote_fraction_of_year) * self.periods_per_year
        vol = mo.ewmvol(self, **kwargs)
        vol = vol * np.sqrt(quote_periods)
        vol[self.isnull()] = np.nan
        vol.name = self.name
        
        return vol
    
    def value_at_risk(self, quantile, freq=None, mirror=False):
        """Calaculate value_at_risk from historic return distribution. 
        
        Note
        ----
        There are numerous ways to calculate value_at_risk; this method only 
        provides one: sampling from the historic return distribution. 
        
        Parameters
        ----------
        quantile: float
            The quantile of the historic returns used to define your VaR. For 
            example for a 2.5% VaR: quantile=.025
        freq: string
            The return frequency to use. freq parameter is passed to 
            ReturnsSeries.resample_returns. Example, for monthly VaR 
            freq='M'.
        mirror: bool, optional, default False
            Calaculate the VaR from the negative of the absolute value of all 
            the data. 
        
        Returns
        -------
        float
            The VaR level for the returns data, calculated for the time 
            frequency defined by freq and the quantile defined by quantile."""
        if freq is None:
            rtns = self
        else:
            rtns = self.resample_returns(freq)
        
        if mirror:
            rtns = rtns.abs() * -1
        
        var = rtns.quantile(quantile)
        
        return var
    
    def sharpe_ratio(self, quote_fraction_of_year=1., 
                     upsample_partial_periods=True):
        """Calculate the Sharpe Ratio of the full-sample of returns. 
        
        Note
        ----
        The definition of Sharpe Ratio for this method is simlply 
        average_return/volatility. This simplified definition is common in 
        practive throughout the investment industry. However, the actual 
        definition of the Sharpe Ratio, as defined by William Sharpe, is 
        (average_return - risk_free_rate)/volatility.
        
        Parameters
        ----------
        quote_fraction_of_year: float, optional, default 1.
            The time period to quote the results in, specified as a fraction 
            of a year. For result in monthly terms quote_fraction_of_year=1/12.
            For result in weekly terms quote_fraction_of_year=1/52.
        upsample_partial_periods: bool, optional, default False
            If the time period covered by the ReturnsSeries is shorter than 
            the time period to average over (as specified by 
            quote_fraction_of_year) use the shorter of the two time periods. 
            If you only have 6 months of data and you request the annual 
            average return with upsample_partial_periods=False, it will 
            return the cumulative return for the whole 6 months but will not 
            annualise it. 
        
        Returns
        -------
        float
            Sharpe Ratio of the returns data expressed for the time period
            specified by quote_fraction_of_year. Default time period is 
            annual Sharpe Ratio."""
        avg_ret = self.average_return(quote_fraction_of_year, 
                                      upsample_partial_periods)
        avg_vol = self.vol(quote_fraction_of_year)
        sr = avg_ret / avg_vol
        
        return sr
    
    def drawdown_days(self):
        """A rolling count of the length of each drawdown in days. 
        
        Note
        ----
        Uses the returnseries.utils.drawdown_days function.
        
        Returns
        -------
        pandas.Series
            index is the same as ReturnsSeries, values are a rolling count of 
            the number of days the returns are in drawdown from previous peak. 
        """
        return ru.drawdown_days(self.drawdowns())
    
    def resample_returns(self, freq):
        """Convert returns to a new frequency, accounting for compounding.
        
        Note
        ----
        Uses pandas.Series.resample method. 
        
        Parameters
        ----------
        freq: string
            The frequency to convert the returns to. Passed as 
            pandas.Series.resample(how=freq), so freq can be an value valid 
            for the how arg. 
        
        Returns
        -------
        ReturnsSeries
            index will reflect the new sampling frequency as specified by the 
            freq arg, values will be the appropriate compounded returns for 
            those periods. """
        acct_curve = self.account_curve()
        with wa.catch_warnings():
            wa.simplefilter('ignore')
            acct_curve = acct_curve.resample(freq, 'last')
        
        start_date = acct_curve.index.min() - dt.timedelta(days=1)
        start_val = pd.Series(1, [start_date], name=self.name)
        acct_curve = start_val.append(acct_curve)
        
        rtn = acct_curve.diff().div(acct_curve.shift(1))
        rtn = rtn[1:]
        periods_per_year = ru.annual_median(rtn)
        rtn = ReturnsSeries(rtn, periods_per_year)
        
        return rtn
    
    def summary(self, funcs=rd.summaries['ts'], name=None):
        """Return summary statistics about the returns.
        
        Note
        ----
        This method is intended to allow users the flexibility to look at 
        summary info of their returns however they wish, and to make those 
        summary stats pretty and easy to read. Users simply define their own 
        list of functions to calculate individual stats and pass in the 
        functions. 
        
        ReturnsSeries.summary and ReturnsSeries.summary_ts provide 
        pre-defined summary stats. 
        
        Parameters
        ----------
        funcs: list
            List of functions. Each function returns a tuple of length 2; 
            first tuple entry is a name/description of the statistic, second 
            tuple entry is the calculated value of the statistics.
        name: str, optional, default None
            name to apply to the pandas.Series that is returned. With default 
            arg of None the result will have the same name as the 
            ReturnsSeries        
        Returns
        -------
        pandas.Series
            Has same lenght as list passed in to the funcs arg, index entries 
            are the names/descriptions returned by each function in funcs, 
            values are the calculated statistics returned by functions in 
            funcs. 
        """
        values = []
        index = []
        for func in funcs:
            idx, value = func(self)
            index.append(idx)
            values.append(value)
        
        if name is None:
            name = self.name
        
        rtn = pd.Series(values, index, name=name)

        return rtn    
    
    def recovery_from_worst(self):
        """Return the length of time it took to recover from worst drawdown.
        
        Note
        ----
        If the returns data does not recover from its worst drawdown then a 
        pandas.tslib.NaTType is retunred.
        
        Returns
        -------
        pandas.tslib.Timedelta, pandas.tslib.NaTType
            Lenght of time it took to recover from worst drawdown, or a
            NaN-like type if the returns data has not recovered from worst 
            drawdown."""
        dd = self.drawdowns()
        worst_date = ru.date_of_worst(dd)
        rtn = ru.days_to_recover(dd, worst_date)
        return rtn
    
    def plot_line(self, log2, shade_dates=None, shade_color='lightblue', 
                  **kwargs):
        """Add line plot of account curve to active plotting figure.
        
        Note
        ----
        This method is intended to make it easy for users to construct thier 
        own custom plots formatted as they like. For a pre-packaged plotting 
        method used ReturnsSeries.plot_perf
        
        Parameters
        ----------
        log2: bool
            Passed to ReturnsSeries.account_curve. If False result will be 
            price-index of compounding returns. If True result will be base-2 
            logarithm (numpy.log2) of price-index. 
        shade_dates: list, optional, default None
            List of tuples, each tuple of length 2, each tuple contains start 
            date and end date of time periods to shade with color.
        shade_color: str, optional, default 'lightblue'
            String specifying the color to use for shade_dates. Accepts any 
            valid matplotlib color name/string.
        kwargs: keywords
            Any keyword arguments to pass to matplotlib.pyplot.plot
        
        Returns
        -------
        list
            Returns a list of matplotlib.lines.Line2D objects"""
        srs = self.account_curve(log2)
        
        line = plt.plot(srs.index, srs.values, label=self.name, **kwargs)
        
        if shade_dates is not None:
            rp.shade_dates(shade_dates, srs, shade_color)
        
        return line        
    
    def plot_perf(self, log2, shade_dates=None, shade_color='lightblue', 
                  yticks_round=1, summary_funcs=rd.summaries['ts'], **kwargs):
        """Predefined plotting method to display relevant performance info.        

        Parameters
        ----------
        log2: bool
            Passed to ReturnsSeries.account_curve. If False result will be 
            price-index of compounding returns. If True result will be base-2 
            logarithm (numpy.log2) of price-index and will reset the y-axis 
            label and y-axis tick labels to reflect the log scale
        shade_dates: list, optional, default None
            List of tuples, each tuple of length 2, each tuple contains start 
            date and end date of time periods to shade with color.
        shade_color: str, optional, default 'lightblue'
            String specifying the color to use for shade_dates. Accepts any 
            valid matplotlib color name/string
        yticks_round: int, optional, default 1
            Number of decimals the y-axis tick lables should be rounded to
        summary_funcs: list, optional, 
        default returnsseries.displayfunctions.summaries['ts']
            list of functions passed into ReturnsSeries.summary
        kwargs: keywords
            Any keyword arguments to pass to matplotlib.pyplot.plot
        
        Returns
        -------
        None"""
        self.plot_line(log2, shade_dates, shade_color, **kwargs)
        
        if log2:
            rp.yticks_log2(round_=yticks_round)
        
        rp.text_topleft(self.summary(summary_funcs).to_string())
        
        plt.title(self.name)
        
        return None
    
    def period_returns(self, periods, within, skip_blanks=False, 
                       period_name_idx=0):
        """Extract the returns for a set of subperiods. 
        
        Parameters
        ----------
        periods: list
            List of tuples, each tuple is of lenght 2, tuple entries are the 
            inclusive start-date and end-date for the time-period to be 
            extracted.
        within: bool
            If True, the returned data will be the all the returns that are 
            within the inclusive time periods defined by periods arg. If False,
            the returned data will be all the returns that are not within 
            inclusive time periods defined by periods arg.
        skip_blanks: bool, optional, default False
            If a time period defined in periods arg results in a ReturnSeries 
            of lenght zero (i.e. no data) do not return this ReturnsSeries. If 
            skip_blanks=False, the returned list always has the same length as 
            periods arg. If skip_blanks=True, the returned list may have lenght
            <= lenght of periods arg
        period_name_idx: int, None
            int specifying which entry in each period tuple to use as the 
            name of the ReturnsSeries that is returned. Generally each tuple 
            should be of length 2 with a start date and end date. Defaults to 
            using the first tuple entry for the name. Set to None and each 
            ReturnsSeries returned will have the same name as the ReturnsSeries
            that created it. 
        
        Returns
        -------
        list
            Returns list of ReturnsSeries objects."""
        rtnl = []
        for period in periods:
            ri = self[ ru.in_range(self.index, period, within) ]
            if skip_blanks and ri.shape[0] < 1:
                continue
            ri = self.__to_returnsseries__(ri)
            if period_name_idx is not None:
                ri.name = period[period_name_idx]
            rtnl.append(ri)
        return rtnl
    
    def period_returns_summaries(self, periods, within, 
                                 summary_funcs=rd.summaries['ts'],
                                 period_name_idx=0):
        """Extract the returns for a set of subperiods. 
        
        Parameters
        ----------
        periods: list
            List of tuples, each tuple is of lenght 2, tuple entries are the 
            inclusive start-date and end-date for the time-period to be 
            extracted.
        within: bool
            If True, the returned data will be the all the returns that are 
            within the inclusive time periods defined by periods arg. If False,
            the returned data will be all the returns that are not within 
            inclusive time periods defined by periods arg
        summary_funcs: list, optional, 
        default returnsseries.displayfunctions.summaries['ts']
                list of functions passed into ReturnsSeries.summary
        period_name_idx: int, None
            int specifying which entry in each period tuple to use as the 
            name of the ReturnsSeries that is returned. Generally each tuple 
            should be of length 2 with a start date and end date. Defaults to 
            using the first tuple entry for the name. Set to None and each 
            ReturnsSeries returned will have the same name as the ReturnsSeries
            that created it. 
        
        Returns
        -------
        list
            list of pandas.Series objects"""
        rtnsl = self.period_returns(periods, within, skip_blanks=True,
                                    period_name_idx=period_name_idx)
        
        rtn = [ x.summary(summary_funcs) for x in rtnsl ]
        
        return rtn

    def periods_combined(self, periods, within):
        """Extract returns for set of subperiods, combine in one ReturnsSeries.
        
        Note
        ----
        In the ReturnsSeries returned by this method the timestamps in the 
        index are meaningless. All of the data is reindexed so the timestamps 
        are continous and finish at the last index value. Any statistics or 
        methods calculated on this ReturnsSeries that rely on the index 
        (ie. ReturnsSeries.summary_ts) will be meaningless. You should only use
        statistics/methods that are correct even if the returns are unordered 
        (ie. ReturnsSeries.cum_return, ReturnsSeries.summary)
        
        Parameters
        ----------
        periods: list
            List of tuples, each tuple is of lenght 2, tuple entries are the 
            inclusive start-date and end-date for the time-period to be 
            extracted.
        within: bool
            If True, the returned data will be the all the returns that are 
            within the inclusive time periods defined by periods arg. If False,
            the returned data will be all the returns that are not within 
            inclusive time periods defined by periods arg.
        
        Returns
        -------
        ReturnsSeries
            All of the return data for the subperiods defined in periods arg 
            is combined into one continuous ReturnsSeries. In the index of this 
            ReturnsSeries the timestamps are basically meaningless. All of the 
            data is reindexed so the timestamps are continous and finish at the 
            last index value."""
        rtn = ru.keep_ranges(self, periods, within)
        rtn = ru.dropna_and_reindex(rtn)
        return rtn
    
    def periods_combined_summary(self, periods, 
                                 names=['all', 'within', 'without'],
                                 summary_funcs=rd.summaries['no_ts']):
        """Extract returns for set of subperiods, combine in one ReturnsSeries.
        
        Note
        ----
        Uses ReturnsSeries.periods_combined method. Results are always 
        calculated as: 1) using all the data 2) using periods and within=True 
        3) using periods and within=False
        
        Parameters
        ----------
        periods: list
            List of tuples, each tuple is of lenght 2, tuple entries are the 
            inclusive start-date and end-date for the time-period to be 
            extracted.
        names: list, optional, default ['all', 'within', 'without']
            list of names to be applied to the returned pandas.Series. list 
            must be of length 3. 
        summary_funcs: list, optional, 
        default returnsseries.displayfunctions.summaries['ts']
            list of functions passed into ReturnsSeries.summary
        
        Returns
        -------
        list
            list of length 3, containing 3 pandas.Series objects"""
        all_ = self.summary(summary_funcs, names[0])
        
        win = self.periods_combined(periods, within=True)
        win = win.summary(summary_funcs, names[1])
        
        wout = self.periods_combined(periods, within=False)
        wout = wout.summary(summary_funcs, names[2])
        
        return all_, win, wout
