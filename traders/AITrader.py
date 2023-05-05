import random
import torch
from .BaseTrader import BaseTrader
from trading_api import StockData, Portfolio
from ml import SimpleCNN
import yaml
from config import path


class AITrader(BaseTrader):
    """
    Class that implements the BaseTrader abstract class.
    It trains a model for every chosen stock, and predicts the next price.
    It buys the stocks with the best predicted price gains.
    """
    def __init__(self, num_picks=25):
        """
        Initialize model parameters and available_symbols.
        :param num_picks: Number of random stocks to predict their price.
        """
        super().__init__()
        self.num_picks = num_picks
        with open(path + "/data/available_stocks.yaml", "r") as f:
            self.available_symbols = yaml.load(f, yaml.FullLoader)

        self.models = {}
        self.symbols = None
        self.sd = None
        self._train_models()

    def _train_models(self):
        """
        Trains a SimpleCNN model for every stock chosen stock and current stocks.
        """
        self.symbols = random.choices(self.available_symbols, k=self.num_picks) + self._get_current_stocks()

        self.sd = StockData(symbols=self.symbols)

        for i, symbol in enumerate(self.symbols):
            self.models[symbol] = SimpleCNN((1, 1, 100))
            # print(symbol)
            # self.models[symbol].debug = True
            self.models[symbol].learn(self.sd.data[:, i].reshape(-1, 1))
            # print("----")

    def _calculate_prices(self):
        """
        Calculates the next price and price gain for the chosen stocks.
        To prevent buying outliers, the gain ratio is 1.0 if the model predicts more than 30% gain or loss.
        :return: prices and price gains
        """

        prices = {}
        diffs = {}
        print("ai forecast:")
        for i, symbol in enumerate(self.symbols):
            prices[symbol] = self.models[symbol](torch.tensor(self.sd.data[-100:, i],
                                                              dtype=torch.float32).reshape(1, 1, 100)).item()
            ratio = prices[symbol] / self.sd.data[-1, i]
            if ratio < 0.7 or ratio > 1.3:  # filter outliers
                ratio = 1.0
            diffs[symbol] = ratio
            print(f"{symbol}: prev: {self.sd.data[-1, i]} forecast: {prices[symbol]}")

        print("-------")

        return prices, diffs

    @staticmethod
    def _get_current_stocks():
        """
        Gets the current stocks on the trading account.
        :return: stock symbol list
        """
        stocks = []

        with Portfolio() as portfolio:
            for s in portfolio.positions:
                stocks.append(s["symbol"])

        return stocks

    def trade(self):
        """
        Method that makes the trade.
        It buys about 1000$ of the best predicted stock.
        If there is less money than 20000, it will sell off stocks with the worst predicted values.
        :return:
        """
        self.log_money()
        prices, gains = self._calculate_prices()

        # getting the best gain
        max_s = 0
        max_gain = -999999999
        for s, g in gains.items():
            if g > max_gain and s not in self._get_current_stocks():
                max_gain = g
                max_s = s

        with Portfolio() as portfolio:
            # at most 1000$
            qty = 1000 // portfolio.get_price(max_s)
            if portfolio.cash > 20000:
                print(portfolio.make_order(max_s, qty, True))
            else:  # if there is less money
                i = 0
                while portfolio.cash < 20000 or i < 20:  # trying to sell off the worst predicted stocks
                    # calculating worst gain
                    min_s = 0
                    min_gain = 999999999
                    for position in portfolio.positions:
                        if gains[position["symbol"]] < min_gain:
                            min_gain = gains[position["symbol"]]
                            min_s = position

                    sell_qty = min(min_s["qty"], 20000 // min_s["price"])

                    # sell
                    portfolio.make_order(min_s["symbol"], sell_qty, False)
                    i += 1

                # trying to buy the selected stock after selloff
                print(portfolio.make_order(max_s, qty, True))
