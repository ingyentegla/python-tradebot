import random
import unittest
from scraper import RedditScraper


class TestRedditScraper(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = RedditScraper()
        self.fake_posts = [{"title": "Stock in title too $GME", "body": "pump $GME!"},
                           {"title": "test title #2", "body": "b*lls deep in META calls"},  # also MET exists
                           {"title": "test title #3", "body": "Proud to be $GME owner"},
                           {"title": "test title #4", "body": "Still Hodlin $GME"},
                           {"title": "HUGE POTENTIAL in $TSLA", "body": "I love daddy elon, buy buy, make daddy proud"},
                           {"title": "test title #6", "body": "Is  buying $AMC still worth it?"},
                           {"title": "test title #6", "body": "$ABCDEFGHIJ does not exist"}]

    def test_init(self):
        self.assertIsNotNone(self.scraper.available_symbols)
        self.assertTrue(isinstance(self.scraper.posts, list))
        self.assertTrue(len(self.scraper.posts) > 0)
        self.assertTrue(isinstance(self.scraper.posts[0], dict))

    def test_get_posts(self):
        posts = self.scraper._get_posts(50)
        self.assertTrue(isinstance(posts, list))
        self.assertTrue(len(posts) > 0)
        self.assertTrue(isinstance(posts[0], dict))
        self.assertTrue(posts[0]["body"] != "")

    def test_get_top(self):
        self.scraper.posts = self.fake_posts
        out = self.scraper.get_top()
        # should be no MET, only META
        self.assertEqual(out, {'GME': 3, 'TSLA': 1, 'AMC': 1, 'META': 1})

    def test_get_max(self):
        self.scraper.posts = self.fake_posts
        self.assertEqual(self.scraper.get_max(), 'GME')
        self.scraper.posts = []
        self.assertEqual(self.scraper.get_max(), 'GME')
        random.seed(1234)  # always returns the 2.
        self.scraper.posts = [{"title": "$TSLA", "body": "$TSLA"},
                              {"title": "--", "body": "$GOOG"},
                              {"title": "--", "body": "$GME"}]

        self.assertEqual(self.scraper.get_max(), "GOOG")
