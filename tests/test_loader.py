import unittest
from trading_api import StockData
import yaml


class TestStockData(unittest.TestCase):
    def setUp(self):
        self.sd = StockData(history_length=365, symbols=["AAPL", "GOOG", "SOMEBSSTOCK"])

    def test_init(self):
        self.assertTrue(self.sd.data.shape[1] == 2 and 365 >= self.sd.data.shape[0] > 200)
        self.assertEqual(self.sd.labels, ["AAPL", "GOOG"])

    def test_many_symbols(self):
        with open("../data/available_stocks.yaml", "r") as f:
            available_symbols = yaml.load(f, yaml.FullLoader)
        symbols = [s for i, s in enumerate(available_symbols) if i < 10]
        allstocks = StockData(symbols=symbols)
        self.assertEqual(allstocks.labels, symbols)
