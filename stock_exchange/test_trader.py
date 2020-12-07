import unittest
from datetime import datetime
from random import randint
from time import sleep

import requests

from stock_exchange.trader import Trader
from unittest.mock import Mock
from requests.exceptions import Timeout



class TestTrader(unittest.TestCase):
    trader = Trader([])

    def test_add_symbol_handle_symbol_quote(self):
        self.trader.handle_symbol_quote("AAPL")
        self.assertIn("AAPL", self.trader.symbols)

    def test_symbol_exists_handle_symbol_quote(self):
        self.assertRaises(Exception, self.trader.handle_symbol_quote, "AAPL")

    def test_symbols_in_connection(self):
        self.trader.handle_symbol_quote("AMZN")
        self.assertIn("AMZN", self.trader._connection.symbols)

    def test_handle_quote_from_nasdaq(self):
        calc = Mock()
        calc.return_value = {'std': 2542, 'max': 24, 'min': 2}
        self.trader.calc = calc

        for i in range(11):
            quote = {'time': datetime.now(), 'symbol': "AAPL", 'price': randint(1, 100)}
            sleep(1)
            self.trader.handle_quote_from_nasdaq(quote)
        self.assertEqual(len(self.trader.quotes.get("AAPL")), 11)
        sleep(1)
        self.assertListEqual(self.trader.quotes.get("AAPL"), [])
        self.assertGreater(len(self.trader.open_positions), 0)

    """
    Sanity Checks
    """

    def test_buy(self):
        balance = self.trader.current_gain
        self.trader.buy("AAPL")
        self.assertLess(self.trader.current_gain, balance)

    def test_sell(self):
        balance = self.trader.current_gain
        self.trader.sell("AAPL")
        self.assertGreater(self.trader.current_gain, balance)

    def test_api_server(self):
        r = requests.get('http://localhost:5000/')
        assert r.status_code == 200

if __name__ == '__main__':
    unittest.main()
