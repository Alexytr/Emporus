from stock_exchange.trader import Trader
from threading import Thread


def main():
    trader = Trader(["AAPL", "FB"])
    try:
        stream = Thread(target=trader.start_data_stream)
        stream.start()
        trader.handle_symbol_quote("PAA")
        stream.join()

    except KeyboardInterrupt:
        trader.stop()

if __name__ == '__main__':
    main()