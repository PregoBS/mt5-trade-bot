from broker_account import BrokerAccountMT5
import api
import bot
from database import TradeDatabase
from datetime import datetime
from dotenv import load_dotenv
import indicators
import os
import pandas as pd
from risk_management import AccountRiskManager, AccountRiskSettings, TradeRiskManager, TradeRiskSettings
import signals
import strategies
from symbols_info import SymbolsInfo, SymbolStrategyConfig, SymbolStrategyInfo
import sys
from typing import List

load_dotenv()
pd.set_option('display.max_columns', 500)  # número de colunas
pd.set_option('display.width', 1500)  # largura máxima da tabela


def mt5_connection(mt5_api: api.MetaTrader5API) -> None:
    mt5_credentials = api.MT5Credentials(path=os.getenv("MT5_PATH") or "",
                                         login=int(os.getenv("MT5_LOGIN")) or 0,
                                         server=os.getenv("MT5_SERVER") or "",
                                         password=os.getenv("MT5_PASSWORD") or "")
    try:
        assert mt5_api.connect(mt5_credentials) is True
    except AssertionError:
        print("API didn't connect")
        sys.exit(1)
    return None


def add_indicators(manager: indicators.Manager) -> None:
    manager.clear()
    manager.add(indicators.ATR("ATR20", 20))
    manager.add(indicators.EMA("EMA3", 3))
    manager.add(indicators.EMA("EMA21", 21))
    manager.add(indicators.EMA("EMA72", 72))
    manager.add(indicators.EMACrossover("EMACrossover3_21", 3, 21))
    return None


def add_signals(manager: signals.Manager) -> None:
    manager.clear()
    manager.add(signals.EMACrossover("EMACrossover", "EMACrossover3_21", shift=1))
    return None


def add_strategies(manager: strategies.Manager, s: List[strategies.Strategy]) -> None:
    manager.clear()
    for strategy in s:
        manager.add(strategy)
    return None


def main(symbols_info: SymbolsInfo) -> None:
    mt5api = api.MetaTrader5API(delta_timezone=-6)
    mt5_connection(mt5api)

    db = TradeDatabase(f"{os.path.dirname(__file__)}/database.db", symbols_info)

    broker_acc = BrokerAccountMT5(mt5api, db)

    trade_bot = bot.TradeBot(mt5api, db, symbols_info)

    trade_risk = TradeRiskManager(trade_bot, symbols_info)

    acc_risk = AccountRiskManager(db, trade_risk, symbols_info)

    indicators_manager = indicators.Manager()
    signals_manager = signals.Manager()

    run = True
    while run:
        try:
            broker_acc.sync_db()

            for symbol in symbols_info.symbols:
                for strategy_info in symbols_info.info[symbol]:
                    for config in strategy_info.configs:
                        # -- CONFIG ACCOUNT RISK MANAGEMENT
                        acc_risk.risk_settings = AccountRiskSettings(capital=config.capital,
                                                                     day_goal=config.day_goal,
                                                                     day_stop=config.day_stop,
                                                                     op_per_day=config.op_per_day)
                        # -- CONFIG TRADE RISK MANAGEMENT
                        trade_risk.symbol_attributes = mt5api.get_symbol_attributes(symbol)
                        trade_risk.risk_settings = TradeRiskSettings(timeframe=config.timeframe,
                                                                     op_goal=config.op_goal,
                                                                     op_stop=config.op_stop)
                        # -- CREATE DATAFRAME AND COMPUTE INDICATORS
                        dataframe = mt5api.create_dataframe_from_bars(symbol, config.timeframe, 0, 100)
                        add_indicators(indicators_manager)
                        dataframe = indicators_manager.compute_all(dataframe)
                        # print(dataframe.tail(3), end="\n\n")
                        # -- COMPUTE SIGNALS
                        add_signals(signals_manager)
                        signals_results = signals_manager.compute_signals(symbol, config.timeframe, dataframe)
                        # print("Signals:", [s.name for s in signals_results], end="\n\n")
                        # -- COMPUTE STRATEGIES
                        strategy = strategy_info.strategy
                        strategy.subscribe(acc_risk)
                        # -- CHECK CURRENT POSITIONS
                        positions = broker_acc.get_positions_by(strategy.magic)
                        for position in positions:
                            strategy.check_protect(position, mt5api, trade_risk)
                            strategy.check_close(position, mt5api, trade_risk)
                        # -- CHECKING THE WAITING TIME BEFORE EACH TRADE CHECK
                        check_interval_minutes = (datetime.today() - config.last_check).seconds // 60
                        if check_interval_minutes > config.wait_to_check:
                            strategy.check_new_position(symbol, config.timeframe, dataframe, signals_results)

        except KeyboardInterrupt:
            run = False

    mt5api.shutdown()
    return None


if __name__ == "__main__":
    s_info = SymbolsInfo()
    s_info.add(SymbolStrategyInfo("BTCUSD",
                                  strategies.EMACrossover("EMACrossover", magic_number=99),
                                  [SymbolStrategyConfig(timeframe="M15",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=10,
                                                        op_stop=5,
                                                        wait_to_check=5),
                                   SymbolStrategyConfig(timeframe="H1",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=20,
                                                        op_stop=10,
                                                        wait_to_check=20)
                                   ]))
    s_info.add(SymbolStrategyInfo("ETHUSD",
                                  strategies.EMACrossover("EMACrossover", magic_number=99),
                                  [SymbolStrategyConfig(timeframe="M15",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=10,
                                                        op_stop=5,
                                                        wait_to_check=5),
                                   SymbolStrategyConfig(timeframe="H1",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=20,
                                                        op_stop=10,
                                                        wait_to_check=20)
                                   ]))
    s_info.add(SymbolStrategyInfo("EURUSD",
                                  strategies.EMACrossover("EMACrossover", magic_number=99),
                                  [SymbolStrategyConfig(timeframe="M15",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=10,
                                                        op_stop=5,
                                                        wait_to_check=5),
                                   SymbolStrategyConfig(timeframe="H1",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=30,
                                                        op_stop=15,
                                                        wait_to_check=20)
                                   ]))
    s_info.add(SymbolStrategyInfo("GBPUSD",
                                  strategies.EMACrossover("EMACrossover", magic_number=99),
                                  [SymbolStrategyConfig(timeframe="M15",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=10,
                                                        op_stop=5,
                                                        wait_to_check=5),
                                   SymbolStrategyConfig(timeframe="H1",
                                                        capital=5000,
                                                        day_goal=0,
                                                        day_stop=0,
                                                        op_per_day=0,
                                                        op_goal=18,
                                                        op_stop=9,
                                                        wait_to_check=20)
                                   ]))
    main(s_info)
