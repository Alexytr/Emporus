import random
import time
import datetime
from typing import List, Dict
from threading import Thread
from threading import Event

from stock_exchange.model import Model
from stock_exchange.nasdaq import StockExchangeProvider

TRADER_USERNAME = 'ploni'
TRADER_PASSWORD = 'Aa123456'

class Trader():
    current_gain = 0

    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self._connection = StockExchangeProvider()
        self.open_positions = []
        self.quotes = {key: [] for key in symbols}
        self._stop = Event()

    def get_current_info(self):
        return {"Current Gain": self.current_gain,
                "Scanned Symbols": self.symbols}

    def calc(self, aggregated_quotes):
        if len(aggregated_quotes) >= 2:
            time.sleep(0.5)
            return {'std': 2542, 'max': 24, 'min': 2}
        else:
            raise Exception('aggregated quotes must have only 10 elements')

    def sell(self, symbol):
        sell_price = random.randint(1, 100)
        self.current_gain += sell_price
        print(f'The symbol: {symbol} was sold')

    def buy(self, symbol):
        buy_price = random.randint(1, 100)
        self.current_gain -= buy_price
        print(f'The symbol: {symbol} was bought')

    def stop(self):
        self._stop.set()


    def _make_a_trade(self, symbol: str, symbol_quotes: List[str]):
        """
        Make a prediction based on the last 10 seconds and buy/sell the stock
        :param symbol: symbol to make the prediction on
        :param symbol_quotes: quotes of the last 10 seconds
        """
        m = Model()
        try:
            is_buy, sell_seconds = m.predict(self.calc(symbol_quotes))
            self.quotes[symbol] = []

            if not self._stop.is_set() and is_buy:
                self.buy(symbol)
                print(f"{symbol}: Selling in {sell_seconds} seconds")
                time.sleep(sell_seconds)
                self.sell(symbol)

        except Exception as e:
            print(f"Got exception while processing quotes for {symbol}: {e}, continuing to the next quotes ..")


    def handle_quote_from_nasdaq(self, quote: Dict[str, int]):
        """
        Handle a quote as soon as we get it from the nasdaq
        :param quote: stock info with {time, symbol, price}
        """
        if self._stop.is_set():
            return

        self.quotes[quote["symbol"]].append(quote)

        for symbol, symbol_quotes in self.quotes.items():
            # not enough quotes
            if len(symbol_quotes) < 2:
                break

            # wait till 10 seconds pass
            if symbol_quotes[-1]["time"] - symbol_quotes[0]["time"] < datetime.timedelta(seconds=10):
                break

            open_position = Thread(target=self._make_a_trade, args=(symbol, symbol_quotes))
            open_position.start()
            self.open_positions.append(open_position)


    def start_data_stream(self):
        """
        The goal here is to keep our connection to the "Nasdaq" alive all the time and make sure there's 0 down time.
        """
        while True:
            self._connection.configure_quotes_stream(self.symbols, self.handle_quote_from_nasdaq)
            self._connection.connect(TRADER_USERNAME, TRADER_PASSWORD)
            try:
                self._connection.start()

            except Exception as e:
                print(f"Connection Failed with error: {e}, ignore and restart connection..")

            for position in self.open_positions:
                position.join()

            if self._stop.is_set():
                self._connection = None
                break


    def handle_symbol_quote(self, symbol_quote: str):
        """
        Receive quote from stock exchange, aggregate 10 seconds of quotes from provided symbols.
        If we have more than 2 quotes and exactly 10 seconds of the symbol we can call 'calc'
        to get the calculated data for model prediction -> call predict -> print if the symbol should be bought.
        You receive quote each millisecond.
        quote is made of : time, symbol, price
       return:
        """
        if symbol_quote in self.symbols:
            return
        self.symbols.append(symbol_quote)
        self.quotes[symbol_quote] = []
        if self._connection:
            self._connection.configure_quotes_stream(self.symbols, self.handle_quote_from_nasdaq)
