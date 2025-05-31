# my_stocks.py
import yfinance as yf
import pandas as pd
from datetime import datetime

def get_portfolio_data():
    portfolio = {
        "BB.TO": {"shares": 5, "buy_price": 5.46},
        "BNS.TO": {"shares": 3, "buy_price": 70.50},
        "DOL.TO": {"shares": 1, "buy_price": 168.19},
        "SHOP.TO": {"shares": 2, "buy_price": 127.00},
        "ENB.TO": {"shares": 4, "buy_price": 62.60},
        "LUN.TO": {"shares": 42, "buy_price": 12.52},
        "VCN.TO": {"shares": 6, "buy_price": 53.46},
        "VFV.TO": {"shares": 4.0209, "buy_price": 143.86},
        "XEG.TO": {"shares": 35.5231, "buy_price": 16.35},
        "XGRO.TO": {"shares": 6, "buy_price": 31.31},
        "XEQT.TO": {"shares": 10, "buy_price": 34.94},
        "CNQ.TO": {"shares": 10, "buy_price": 42.88},
        "VUN.TO": {"shares": 0.8173, "buy_price": 108.97},
        "WCP.TO": {"shares": 64, "buy_price": 8.90},
        "FFU.V": {"shares": 291, "buy_price": 0.0676},
        "KDOZ.V": {"shares": 35, "buy_price": 0.3766},
    }

    unlisted_stock = 0.00
    start_date = "2025-05-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    tickers = list(portfolio.keys())
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    if isinstance(data, pd.Series):
        data = data.to_frame()

    portfolio_value = pd.Series(unlisted_stock, index=data.index)
    for ticker, info in portfolio.items():
        if ticker in data.columns:
            portfolio_value += data[ticker] * info['shares']

    initial_value = sum(info["shares"] * info["buy_price"] for info in portfolio.values()) + unlisted_stock
    latest_value = portfolio_value.iloc[-1]
    growth = 100.0 * (latest_value - initial_value) / initial_value

    days_held = (datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")).days
    years_held = days_held / 365.0

    return portfolio_value, initial_value, latest_value, growth, years_held

