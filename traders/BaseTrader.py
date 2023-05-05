from abc import ABC, abstractmethod
import datetime
import threading
from trading_api import Portfolio
from config import path


class BaseTrader(ABC):
    """
    Base class for traders. This class handles trading.
    """
    def __init__(self):
        """
        Initializes thread for
        """
        # init thread
        self._thread = threading.Timer(60, self.do)
        self._thread.start()

    def do(self):
        """
        Helper function that calls periodically after a delay self.trade()
        """
        with Portfolio() as pf:
            if pf.market_open:
                print(f"calling trade(): {datetime.datetime.now()}")
                self.trade()
        self._thread.cancel()
        self._thread = threading.Timer(60, self.do)
        self._thread.start()

    def __del__(self):
        self._thread.cancel()
        print("DEL")

    @staticmethod
    def _dummy():
        """
        Helper function for debugging threading.
        """
        print(f"dummy called: {datetime.datetime.now()}")

    @staticmethod
    def log_money():
        """
        Logs total equity before every trade. The logs will be used to generate charts.
        """
        with open(path + "/data/portfolio.yaml", "a") as fp:
            with Portfolio() as portfolio:
                fp.write(f"- {portfolio.total_equity}\n")

    @abstractmethod
    def trade(self):
        """
        This function is called periodically. It decides which stocks to buy and/or sell.
        Abstract method, has to be implemented in child classes.
        """
        pass
