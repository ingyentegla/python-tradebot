import yaml
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import numpy as np
from config import path


class StockData(object):
    """
    Class representing historical stock data. Loads data from the api.
    Important: the data from the api is sometimes incorrect.
    """
    def __init__(self, api_key=None, secret_key=None, history_length=365, symbols=None):
        if api_key is None or secret_key is None:
            with open(path + "/data/keys.yaml", "r") as f:
                keys = yaml.load(f, yaml.FullLoader)
                api_key, secret_key = keys['api_key'], keys['secret_key']

        with open(path + "/data/available_stocks.yaml", "r") as f:
            available_symbols = yaml.load(f, yaml.FullLoader)

        # check available stocks
        if symbols is None or (isinstance(symbols, (list, tuple)) and len(symbols) == 0):
            symbols = available_symbols
        else:
            new_symbols = []
            for s in symbols:
                if s in available_symbols:
                    new_symbols.append(s)

            symbols = new_symbols

        # load historical data
        end_date = datetime.now() - timedelta(days=1)  # cannot get current data with a free account
        start_date = end_date - timedelta(days=history_length)

        # historical data is not reliable, only meant for debugging, use e.g. polygon.io instead
        stock_client = StockHistoricalDataClient(api_key, secret_key)
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )
        bars = stock_client.get_stock_bars(request_params)

        # get actual labels in bars
        self._labels = []
        max_len = 0
        for s in symbols:
            try:
                if len(bars[s]) > max_len:
                    max_len = len(bars[s])
                self._labels.append(s)
            except KeyError as e:
                print(e)

        if len(self._labels) == 0:
            raise ValueError("There are no labels!")

        # fill numpy array with closing prices and pad missing data with zeros
        self._data = np.zeros((max_len, len(self._labels)))
        for i, l in enumerate(self._labels):
            self._data[-len(bars[l]):, i] = np.array([b.close for b in bars[l]])

    @property
    def data(self):
        return self._data

    @property
    def labels(self):
        return self._labels
