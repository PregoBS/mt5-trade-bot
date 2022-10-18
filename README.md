# MT5 Trade Bot

MT5 Trade Bot is a Python project for traders who want to automate their trading operations in MetaTrader 5.

The objective is to make a template that improves the implementation of different strategies.

The trader will not need to worry about the MetaTrader5 API code.

Just implement your own Indicators and Strategies following the Interfaces.

## Project Status

Under development.
- Currently Working!

## Available Features
### Indicators
<sup>**Indicators** (historical data): computed in pandas DataFrame based on _OHLC prices_ and/or another _Indicators_</sup>
- ATR (Average True Range)
- EMA (Exponential Moving Average)
- EMA_Crossover (Exponential Moving Average Crossover)

### Signals
<sup>**Signals** (data structure containing one signal): computed based on _Indicators_ </sup>
- EMA_Crossover (Exponential Moving Average Crossover)

### Strategies
<sup>**Strategies**: computed based on one or more _Signals_</sup>
- EMA_Crossover (Exponential Moving Average Crossover)

.

.

.

Feel free to clone the repository and test your own Strategies.

(Recommended to test using Demo Accounts!)

## License
[MIT](https://choosealicense.com/licenses/mit/)