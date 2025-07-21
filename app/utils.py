import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_history(symbol, period="3mo"):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    df = df.reset_index()
    df.rename(columns={"Date": "date", "Open": "open", "High": "high",
                       "Low": "low", "Close": "close", "Volume": "volume"}, inplace=True)
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["daily_return"] = df["close"].pct_change() * 100
    return df
