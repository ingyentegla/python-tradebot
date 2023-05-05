import unittest
from trading_api import Portfolio


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()

    def test_context_manager(self):
        # should not raise error
        with Portfolio(api_key="wrong key") as pf:
            pass

        with Portfolio() as pf:
            self.assertEqual(1, 1)  # enters the with statement
            pf.cash = 10  # suppress error

    def test_is_available(self):
        self.assertTrue(self.portfolio.is_available("AAPL"))
        self.assertFalse(self.portfolio.is_available("NONEXISTENTSTOCK"))

    def test_get_price(self):
        self.assertTrue(isinstance(self.portfolio.get_price("AAPL"), float))

    def test_properties(self):
        self.assertTrue(isinstance(self.portfolio.cash, float))
        self.assertTrue(isinstance(self.portfolio.total_equity, float))
        self.assertTrue(isinstance(self.portfolio.market_open, bool))

    def test_positions(self):
        positions = self.portfolio.positions
        self.assertTrue(isinstance(positions, list))
        if len(positions) > 0:
            self.assertTrue(isinstance(positions[0], dict))
