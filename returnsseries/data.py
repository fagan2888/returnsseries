"""Read and clean data to use in examples. Data from Yahoo Finance."""
import os
import pandas as pd

_current_folder_ = os.path.abspath(os.path.dirname(__file__)) 

_spx_file_ = os.path.join(_current_folder_, r'data/spx_sp_500_index.csv')

spx = pd.read_csv(_spx_file_, header=0, index_col=0, parse_dates=[0], 
                  dayfirst=True)
spx = spx.sort_index().loc[:,'Close'].resample('M').last()
spx = spx.div( spx.shift(1) ) - 1

_ixr_file_ = os.path.join(_current_folder_, 
                          r'data/ixr_sp_consumer_staples_index.csv')

ixr = pd.read_csv(_ixr_file_, header=0, index_col=0, parse_dates=[0], 
                  dayfirst=True)
ixr = ixr.sort_index().loc[:,'Close']
ixr = ixr.div( ixr.shift(1) ) -1 
