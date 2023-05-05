from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import alpaca_trade_api as trade_api
import yaml
from config import path


class Portfolio(object):
    """
    Class representing the portfolio. It communicates with the trading api.
    Used for getting the current stock prices, open positions, list open orders, and making new orders.
    """
    def __init__(self, api_key=None, secret_key=None):
        """
        Initializes the api. If no api keys are given, loads it from the config file.
        """
        if api_key is None or secret_key is None:
            with open(path + "/data/keys.yaml", "r") as f:
                keys = yaml.load(f, yaml.FullLoader)
                api_key, secret_key = keys['api_key'], keys['secret_key']

        self.trading_client = TradingClient(api_key, secret_key, paper=True)
        self.api = trade_api.REST(api_key, secret_key, 'https://paper-api.alpaca.markets')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # closing api
        self.api.close()
        return True

    def is_available(self, symbol):
        """
        Returns if as tock is available to trade.
        :param symbol: Symbol of stock
        :return: true, if available
        """
        with open(path + "/data/available_stocks.yaml", "r") as f:
            available_symbols = yaml.load(f, yaml.FullLoader)

        if symbol not in available_symbols:
            return False

        asset = self.trading_client.get_asset(symbol)

        return asset.tradable

    def get_price(self, symbol):
        """
        Gets the current price of a stock
        :param symbol: Symbol of stock
        :return: price
        """
        symbols = [symbol]
        return float(self.api.get_latest_quotes(symbols)[symbol].ap)

    @property
    def market_open(self):
        """
        :return: True if market is open.
        """
        return self.api.get_clock().is_open

    @property
    def cash(self):
        """
        :return: Returns total available cash in the trading account.
        """
        return float(self.trading_client.get_account().cash)

    @property
    def total_equity(self):
        """
        :return: Total equity.
        """
        return float(self.trading_client.get_account().equity)

    @property
    def positions_raw(self):
        """
        :return: Open positions provided by the api.
        """
        return self.api.list_positions()

    @property
    def open_orders(self):
        """
        Returns the open positions.
        :return: Returns a list of dictionaries with position information (symbol, quantity).
        """
        _open_orders = self.api.list_orders(
            status='open',
            limit=100,
        )

        ret = []

        for o in _open_orders:
            ret.append({"symbol": o.symbol, "qty": float(o.qty)})

        return ret

    @property
    def positions(self):
        """
        :return: Returns the open positions in an easily accessible form.
        """
        pos = self.api.list_positions()
        _positions = []
        for p in pos:
            _positions.append({"symbol": p.symbol, "qty": float(p.qty), "price": float(p.current_price)})

        return _positions

    def make_order(self, symbol, qty, buy=True):
        """
        Opens a market order. The opened order has a day to be fulfilled, after that it is deleted.
        :param symbol: Symbol
        :param qty: quantity
        :param buy: buy if true, else sell
        :return: False if the order can't be made. Otherwise, returns some data about the order.
        """

        if not isinstance(symbol, str) or not isinstance(qty, (int, float)):
            return False

        if not self.market_open:
            return False

        # check availability
        if not self.is_available(symbol):
            return False

        # check money
        if 1.1 * self.get_price(symbol) * qty > self.cash - 1000:
            return False

        # make request object
        buy_or_sell = OrderSide.BUY if buy else OrderSide.SELL
        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            qty=qty,
                            side=buy_or_sell,
                            time_in_force=TimeInForce.DAY
        )

        # make order
        market_order = self.trading_client.submit_order(
                       order_data=market_order_data
        )

        return market_order

    def __str__(self):
        s = f"Portfolio: {self.__class__}\n"
        for property_name, value in self.trading_client.get_account():
            s += f"\"{property_name}\": {value}\n"

        return s

