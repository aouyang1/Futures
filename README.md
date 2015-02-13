# Futures Backtester

## Modular algorithmic trading backtester using historical tick level data replayed through various strategies.

Futures Backtester is a tool to help quickly asses the viability of any trading strategy working off of Range bars, a price action candlestick formation. More information on Range Bars can be found here: [Investopedia](http://www.investopedia.com/articles/trading/10/range-bar-charts-different-view.asp)

Tick level data were downloaded using Rithmic as the data provider through a third-party trading platform, NinjaTrader. Historical tick data up to around September of 2013 for Gold futures (GC), Crude Oil futures (CL), and 30-year Treasury Bonds futures (ZB) are currently stored in a MySQL database.

![fad] (figures/gui.png)
![fad] (figures/playback_chart.png)

## Futures Algorithmic Development GUI 
The Python GUI allows users to interactively set backtesting parameters such as instrument, range bar size, date range to test, and strategies to test through a crude editor. Each strategy should have a fixed Profit Target and fixed Stop Loss. Multiple strategies can be run at the same time, but must be specified through the editor. New strategies and/or indicators may be included with the backtester by adding additional classes to the strategy.py and indicator.py files. After each backtest, trade data will be written into a dropbox folder for further analysis in a similar format to the Ninjatrader trade data.

## Setting up Strategies and Indicators
File can be modified through setup_backtest.py or through the GUI.

Multiple strategies can be tested at the same time to save time and allow one-to-one comparisons of the trade data. Care should be taken when specifying multiple strategies working off the same indicators with the same parameters. For example if N strategies are to be tested with various parameters such as ranging profit targets but work off the same indicator with a lookback period of 15 bars, all the strategies should reference the same indicator instead of declaring the same indicator N times.
Example:
```
indicators = {}
indicators['FT'] = FisherTransform(bt, bt.range_bar.Close, 15)
indicators['FTD'] = Diff(bt, indicators['FT'].val, 2)

for PL in range(17, 25):
    bt.strategies['FT_Quicky_Base_PL' + str(PL)] = FT_Quicky_Base(backtest=bt,
                                                                  indicators=indicators,
                                                                  PL=PL,
                                                                  offset=3,
                                                                  FTdthresh=0.1,
                                                                  FTthresh=2.5,
                                                                  maxBars=1)
```

### MySQL Data Storage
update_database_TICK.py - script to parse and place tick data for GC, CL, and ZB onto a mySQL database
update_database_TICK_norepeats.py - script to compress data set for repeated tick values

## Usage
1. python fad.py
2. Select Range Bar size
3. Select Instrument (GC/CL/ZB)
4. Select Date range
5. Click Run

