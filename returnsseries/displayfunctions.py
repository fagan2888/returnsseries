"""funcs passed into ReturnsSeries.summary_funcs for pretty summary stats"""

def ann_rtn(x):
    return 'Annual Return (%)', round(x.average_return(1., False)*100, 1)

def cum_rtn(x):
    return 'Cumulative Return (%)', round(x.cum_return()*100, 1)

def ann_vol(x):
    return 'Annual Volatility (%)', round(x.vol(1.)*100, 1)

def ann_sr(x):
    return 'Sharpe Ratio', round(x.sharpe_ratio(1., False), 2)

def wdd_p(x):
    return 'Worst Drawdown (%)', round(x.drawdowns().min()*100, 0)

def wdd_d(x):
    res = x.index[x.drawdowns() == x.drawdowns().min()][0].date()
    return 'Worst Drawdown Date', res
    
def ttr(x):
    try:
        res = x.recovery_from_worst().days
    except AttributeError:
        res = 0
    res = round(res/30.4375, 0)
    return 'Time to Recover (Mths)', res

def ldd(x):
    res = round(x.drawdown_days().max()/30.4375,0)
    return 'Longest Drawdown (Mths)', res

def ldd_ed(x):
    res = x.index[x.drawdown_days()==x.drawdown_days().max()][0].date()
    return 'Longest Drawdown End', res

def start(x):
    return 'Start Date', x.index.min().date()

def end(x):
    return 'End Date', x.index.max().date()

def tr(x):
    return 'Track Record (Yrs)', round(x.track_record_days()/365.,1)

summaries = {
        'ts' : (cum_rtn, ann_rtn, ann_vol, ann_sr, wdd_p, wdd_d, ttr, ldd, 
                ldd_ed, start, end, tr),
        'no_ts' : (cum_rtn, ann_rtn, ann_vol, ann_sr, tr),
        }
