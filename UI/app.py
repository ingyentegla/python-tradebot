from flask import Flask, render_template, request, redirect
from trading_api import Portfolio
import yaml
from traders import WSBTrader, AITrader
import matplotlib.pyplot as plt
import alpaca_trade_api as trade_api
from config import path

app = Flask(__name__)

mode = "wsb-mode"
trader = None

errors = {"keys": "Wrong keys!", "order": "Could not make order!"}

@app.route('/')
def home():
    """
    Homepage for user interface.
    Shows a chart of the total value of the trading account and the open positions.
    """
    with open(path + "/data/portfolio.yaml", "r") as fp:
        data = yaml.load(fp, yaml.FullLoader)
        plt.plot(data)
        plt.savefig("static/portfolio.png", dpi=100)
    return render_template("home.html", portfolio=Portfolio(), mode=mode)


@app.route("/", methods=["POST"])
def post_home():
    global mode, trader
    data = {}
    for k, v in request.form.items():
        data[k] = v

    mode = data["button"]
    trader.__del__()
    trader = AITrader() if mode == "ai-mode" else WSBTrader()
    return redirect("/")


@app.route("/secret")
def secret():
    """
    Page for changing the api keys
    """
    return render_template("secret.html")


@app.route("/secret", methods=["POST"])
def post_secret():
    data = {}
    for k, v in request.form.items():
        data[k] = v

    try:
        api = trade_api.REST(data['api_key'], data["secret_key"], "https://paper-api.alpaca.markets")
        api.list_positions()  # causes an error if the keys are wrong
        api.close()
    except Exception as e:
        print("EXCEPTION")
        return redirect("/error/keys")

    if data['api_key'] is not None and data["secret_key"] is not None:
        with open(path + "/data/keys.yaml", "w") as fp:
            yaml.dump({"api_key": data["api_key"], "secret_key": data["secret_key"]}, fp)

    return redirect("/")


@app.route("/manual")
def manual_trading():
    """
    Page for manually buying and selling stocks.
    """
    return render_template("manual_trading.html", portfolio=Portfolio())


@app.route("/error/<msg>", methods=["GET"])
def error(msg):
    if msg in errors:
        err = errors[msg]
    else:
        err = ""
    return render_template("error_page.html", message=err)


@app.route("/manual", methods=["POST"])
def post_manual():
    data = {}
    for k, v in request.form.items():
        data[k] = v

    with Portfolio() as pf:
        success = pf.make_order(data["symbol"], float(data["quantity"]), data['button'] == "buy")

    if not success:
        return redirect("/error/order")

    return redirect("/manual")


if __name__ == '__main__':
    trader = AITrader() if mode == "ai-mode" else WSBTrader()
    # trader.trade()

    app.run(debug=False, host="127.0.0.1")
