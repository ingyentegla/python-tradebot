import random
import re
import requests
import yaml
from config import path


class RedditScraper(object):
    """
    Class for scraping r/wallstreetbets.
    Implemented as a context manager, to handle errors.

    """
    def __init__(self):
        with open(path + "/data/available_stocks.yaml", "r") as f:
            self.available_symbols = yaml.load(f, yaml.FullLoader)

        self.posts = self._get_posts(500)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    @staticmethod
    def _get_posts(posts):
        """
        Gets the top pots from reddit and saves it in a list.
        :param posts: number of posts to scrape
        :return: List of posts that have a "body"
        """
        url = f"https://www.reddit.com/r/wallstreetbets/top/.json?limit={posts}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/84.0.4147.105 Safari/537.36'}

        page = requests.get(url, headers=headers)
        page.raise_for_status()
        data = page.json()

        all_posts = []
        for post in data["data"]["children"]:
            all_posts.append(dict(title=post["data"]["title"], body=post["data"]["selftext"]))

        filtered_posts = []
        for item in all_posts:
            if str(item["body"]) != "":
                filtered_posts.append(dict(title=item["title"], body=item["body"]))

        return filtered_posts

    def get_top(self):
        """
        Finds mentioned stocks in the post title and body with regex. Only available stocks are allowed.
        :return: Retunrs the mentioned stocks with their occurrences in a dictionary.
        """
        symbol_dict = {}

        for post in self.posts:
            for symbol in self.available_symbols:
                if re.search(f"{symbol}( |$|\n)", post["body"]) or re.search(f"{symbol}( |$|\n)", post["title"]):
                    if symbol in symbol_dict:
                        symbol_dict[symbol] += 1
                    else:
                        symbol_dict[symbol] = 1

        return symbol_dict

    def get_max(self):
        """
        Finds the most mentioned stock(s) in the scraped posts. If there are more than one, choses one randomly.
        If somehow no stocks were mentioned, returns 'GME', since it is always a good choice for WSB.
        :return: Symbol of the most mentioned stock
        """
        symbol_dict = self.get_top()
        if len(symbol_dict) == 0:
            return "GME"

        max_val = max(symbol_dict.values())

        top = []

        for symbol, val in symbol_dict.items():
            if val == max_val:
                top.append(symbol)

        return random.choice(top)
