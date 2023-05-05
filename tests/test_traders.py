import time
import unittest
from ml import SimpleCNN
from traders import WSBTrader, AITrader
import threading


class TestWSBTrader(unittest.TestCase):
    def setUp(self):
        self.wsbtrader = WSBTrader()

    def tearDown(self):
        self.wsbtrader._thread.cancel()

    def test_threading(self):
        self.assertTrue(threading.active_count() == 2)
        self.wsbtrader._thread.cancel()
        time.sleep(10)  # wait for thread to be cancelled
        self.assertTrue(threading.active_count() == 1)

    def test_trade(self):
        pass


class TestAITrader(unittest.TestCase):
    def setUp(self):
        self.aitrader = AITrader(num_picks=5)

    def tearDown(self):
        self.aitrader._thread.cancel()

    def test_train_models(self):
        self.aitrader._train_models()
        self.assertIsNotNone(self.aitrader.symbols)
        self.assertIsNotNone(self.aitrader.sd)
        self.assertTrue(isinstance(self.aitrader.models, dict))
        self.assertTrue(isinstance(self.aitrader.models[self.aitrader.symbols[0]], SimpleCNN))

    def test_calculate_prices(self):
        self.aitrader._train_models()
        prices, diffs = self.aitrader._calculate_prices()
        for k, v in diffs.items():
            self.assertTrue(0 <= v and isinstance(v, float))
