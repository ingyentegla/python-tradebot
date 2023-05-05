import random
from .BaseTrader import BaseTrader
from scraper import RedditScraper
from trading_api import Portfolio


class WSBTrader(BaseTrader):
    """
    Class that implements the BaseTrader abstract class.
    It represents the r/WallStreetBets trading strategy. It will buy the most mentioned stock on r/wallstreerbets.
    """

    def __init__(self):
        super(WSBTrader, self).__init__()

    def trade(self):
        """
        Method to make a trade. If there is enough money on the current trading account,
        it will buy at most 1000$ of the most mentioned stock on WSB.
        If there isn't enough money, it will sell random stocks until making an order.
        """
        self.log_money()
        with RedditScraper() as rs:
            stock_to_buy = rs.get_max()

            with Portfolio() as portfolio:
                qty = 1000 // portfolio.get_price(stock_to_buy)

                if portfolio.cash > 20000:
                    print(portfolio.make_order(stock_to_buy, qty, True))
                else:
                    i = 0
                    while portfolio.cash < 20000 or i < 20:
                        stock_to_sell = random.choice(portfolio.positions)

                        sell_qty = min(stock_to_sell["qty"], 20000 // stock_to_sell["price"])

                        portfolio.make_order(stock_to_sell["symbol"], sell_qty, False)

                    print(portfolio.make_order(stock_to_buy, qty, True))
