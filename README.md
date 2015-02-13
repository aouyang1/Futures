# Futures Backtester
======================================

## Algorithmic trading backtester using historical tick level data replayed through a chosen strategy.

Futures Backtester is a tool to help quickly asses the viability of any trading strategy working off of Range bars, a price action candlestick formation. More information on Range Bars can be found here: [Investopedia](http://www.investopedia.com/articles/trading/10/range-bar-charts-different-view.asp)

Tick level data were downloaded using Rithmic as the data provider through a third-party trading platform, NinjaTrader. Historical tick data up to around September of 2013 for Gold futures (GC), Crude Oil futures (CL), and 30-year Treasury Bonds futures (ZB) are currently stored in a MySQL database.

# Futures Algorithmic Development (fad) 
The Python GUI allows users to interactively set backtesting parameters such as instrument, range bar size, date range to test, and strategies to test through a crude editor. 

## Usage
1. python fad.py
2. Select Range Bar size
3. Select Instrument (GC/CL/ZB)
4. Select Date range
5. Click Run

