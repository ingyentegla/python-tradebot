import torch
from abc import ABC, abstractmethod


class BaseModel(torch.nn.Module, ABC):
    """
    Base class for models.
    Can be used as a torch.nn.Module with extra training and test functions.
    """

    def __init__(self, input_shape):
        super(BaseModel, self).__init__()
        if input_shape[-1] != 100 or len(input_shape) != 3 or input_shape[-2] != 1:
            raise ValueError("Wrong input shape!")

        self.debug = False

    @abstractmethod
    def forward(self, x):
        pass

    def learn(self, stock_data_orig, test_size=100):
        """
        Training the model. Does not train on the last 'test_size' number of data.
        :param stock_data_orig: np.array, shape=(n,1), where n = number of datapoints
        :param test_size: test size
        """
        stock_data = torch.tensor(stock_data_orig, dtype=torch.float32).permute((1, 0))

        opt = torch.optim.Adam(self.parameters())
        criterion = torch.nn.MSELoss()

        if self.debug:
            print(f"Training {self.__class__} model.")
            # print(self)

        for epoch in range(5):
            self.train()
            for i in range(0, stock_data.shape[1] - 100 - test_size):
                inp = stock_data[:, i:(i+100)].reshape(stock_data.shape[0], 1, -1)
                out = self.__call__(inp)
                y = stock_data[:, i+100]

                loss = criterion(out, y)

                opt.zero_grad()
                loss.backward()
                opt.step()

            if self.debug:
                self.eval()
                print(f"{epoch}.epoch: {self.test(stock_data_orig, test_size)}")

    def test(self, stock_data_orig, test_size=100):
        """
        Tests the model on the test data. It uses the previous 100 observations, to predict the next value.
        It repeats this for the entire test set.
        :param stock_data_orig: stock data, np.array, shape = (x, 1), x >= 100 + test-size
        :param test_size: Length of test set. The last test_size values in the data
        :return: returns the mean absolute error on the test set.
        """
        stock_data = torch.tensor(stock_data_orig, dtype=torch.float32).permute((1, 0))

        criterion = torch.nn.L1Loss()  # mean absolute error

        with torch.no_grad():
            vals = torch.empty(stock_data.shape[0], test_size)
            y = torch.empty(stock_data.shape[0], test_size)

            # predicting next value
            for i in range(test_size, 0, -1):  # test_size -> 1
                inp = stock_data[:, (-i - 100):-i].reshape(stock_data.shape[0], 1, -1)
                vals[:, -i] = self.__call__(inp)  # predict -i from previous 100 values
                y[:, -i] = stock_data[:, -i]

        return criterion(vals, y).detach().item()


class SimpleCNN(BaseModel):
    """
    Simple CNN model for predicting furture stock price.
    """

    def __init__(self, input_shape):
        super(SimpleCNN, self).__init__(input_shape)
        self.conv1 = torch.nn.Conv1d(1, 6, kernel_size=(3,))
        self.conv2 = torch.nn.Conv1d(6, 12, kernel_size=(10,), stride=(5,))
        self.conv3 = torch.nn.Conv1d(12, 16, kernel_size=(5,), stride=(3,))
        self.conv4 = torch.nn.Conv1d(16, 20, kernel_size=(5,), stride=(5,))

        self.linear1 = torch.nn.Linear(20, 1)

    def forward(self, x):
        x = torch.nn.functional.relu(self.conv1(x))
        x = torch.nn.functional.relu(self.conv2(x))
        x = torch.nn.functional.relu(self.conv3(x))
        x = torch.nn.functional.relu(self.conv4(x))
        x = x.flatten(-2)
        x = self.linear1(x)
        return x.reshape(-1)


class CNN2(BaseModel):
    """
    A different CNN model.
    """

    def __init__(self, input_shape):
        super(CNN2, self).__init__(input_shape)
        self.conv1 = torch.nn.Conv1d(1, 12, kernel_size=(5,), stride=(2,))
        self.conv2 = torch.nn.Conv1d(12, 24, kernel_size=(10,), stride=(6,))
        self.conv3 = torch.nn.Conv1d(24, 40, kernel_size=(7,), stride=(7,))
        self.linear1 = torch.nn.Linear(40, 1)

    def forward(self, x):
        x = torch.nn.functional.relu(self.conv1(x))
        x = torch.nn.functional.relu(self.conv2(x))
        x = torch.nn.functional.relu(self.conv3(x))
        x = x.flatten(-2)
        x = self.linear1(x)
        return x.reshape(-1)
