import yfinance as yf
import pandas as pd
import yaml
import uuid

class TradingEngine:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            self.rules = yaml.safe_load(f)

    def fetch_data(self):
        tickers = self.rules["DEFAULT_TICKERS"]
        data = {}
        for t in tickers:
            info = yf.Ticker(t).history(period="1d", interval="1m").tail(5)
            data[t] = info["Close"].iloc[-1]
        return pd.DataFrame.from_dict(data, orient="index", columns=["Price"])

    def make_decision(self, df):
        # Example: Buy if price < buy_threshold
        decisions = {}
        for t in df.index:
            price = df.loc[t, "Price"]
            threshold = self.rules["BUY_THRESHOLDS"].get(t, None)
            if threshold and price < threshold:
                decisions[t] = "BUY"
            else:
                decisions[t] = "HOLD"
        return decisions

    def execute_trade(self, decisions):
        # Fake ticket for now
        return {"ticket_id": str(uuid.uuid4()), "decisions": decisions}
