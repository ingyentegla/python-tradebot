# Automatic stock trader bot to loose all your money

## Installation
Clone the repo
```
git clone https://github.com/ingyentegla/python-tradebot.git
```

Instal requirements
```
pip install -r requirements.txt
```

**Change project directory in config.py** (I know it's not nice, but it's a last minute solution...)


**Change your alpaca-api keys in data/keys.yaml**

Run UI/app.py in pycharm.


You can acces the user interface at http://127.0.0.1:5000/

## About the project
It is an automatic stock trading bot that automatically makes 2 trades every day the market is open. 
There are two trading modes:
- ai-mode: A simple model predicts the future stock prices, and chooses the best.
- wsb-mode: Scrapes r/wallstreetbets and buys the most mentioned stock.
There is also a simple UI where you can trade stock manually, change the api keys or track your portfolio.

## Implementation details
For the trading, I used alpaca-api. The api calls are wrapped in context manager classes, to catch possible errors.

The trading is done with trader classes that inherit from BaseTrader abstract class. The trade() method is the "brain" of the trade bot. It decides which stocks to sell and/or buy every time it's called. The trade() method is managed in a different thread (to allow the ui to be interactive) that is called periodically to make a trade. A new trading strategy can be added simpy by inheriting from the BaseTrader class and calling it from the app.py and maybe including it in the ui.

The scraper simply downloads all all the posts from r/wallstreetbets, and looks for stock names in the post titles and body-s. It calculates which sock was mentioned in the most posts, and buys that. If there is not enough money on your account, it tries to sell random stocks, and then buy if it's possible.

In the ai-mode I used pytorch, to train a CNN model for every stock. it predicts the next price from the previous 100 days. When trading, it chooses the stock, that has the best predicted gain. It's implemnted in a way, that's easy to extend with new models.

In both trading modes, the bot tries to buy at most 1000$ of stocks if possible.

The ui is written in flask.

There are also basic unittest cases for simple testing. The tests are not 100% complete. Functions that make api calls are only tested for return types and simple cases.
