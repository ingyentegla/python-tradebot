from ml import SimpleCNN, CNN2
import unittest
import torch
import numpy as np


class TestCNNModels(unittest.TestCase):
    def setUp(self):
        self.model = SimpleCNN((1, 1, 100))
        self.model2 = CNN2((1, 1, 100))

    def test_init(self):
        self.assertTrue(isinstance(self.model.conv1, torch.nn.Conv1d))
        self.assertTrue(isinstance(self.model.linear1, torch.nn.Linear))

        self.assertTrue(isinstance(self.model2.conv1, torch.nn.Conv1d))
        self.assertTrue(isinstance(self.model2.linear1, torch.nn.Linear))

    def test_forward(self):
        inp = torch.ones((1, 1, 100))
        self.assertTrue(self.model.forward(inp).shape == (1,))

        self.assertTrue(self.model2.forward(inp).shape == (1,))

    def test_test(self):
        inp = np.ones((250, 1))
        self.assertTrue(isinstance(self.model.test(inp), float))

        self.assertTrue(isinstance(self.model2.test(inp), float))

    def test_learn(self):
        t0 = self.model.test(np.ones((250, 1)))
        self.model.learn(np.ones((250, 1)))
        t1 = self.model.test(np.ones((250, 1)))
        self.assertTrue(t0 > t1)

        inp = np.ones((250, 1))
        t0 = self.model2.test(inp)
        self.model2.learn(inp)
        t1 = self.model2.test(inp)
        self.assertTrue(t0 > t1)
