from flask import Flask

from stock_exchange.trader import Trader
from threading import Thread
from flask import Flask, jsonify

app = Flask(__name__)

trader = Trader(["AAPL", "FB"])

@app.route('/', methods=['GET'])
def api_info():
    return jsonify(trader.get_current_info())


def start_server():
    """
    Start our flask Rest API server
    """
    server = Thread(target=app.run, args=())
    server.setDaemon(True)
    server.start()


def start_trader():
    """
    Start our trader
    """
    try:
        stream = Thread(target=trader.start_data_stream)
        stream.start()
        trader.handle_symbol_quote("NIO")
        stream.join()

    except KeyboardInterrupt:
        trader.stop()

        # Stop our daemon server
        exit(0)


    start_server()
    start_trader()
