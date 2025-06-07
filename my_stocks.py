# my_stocks.py
import yfinance as yf
import pandas as pd
from datetime import datetime


def get_portfolio_data(csv_file='portfolio.csv'):
    # Read portfolio purchase info
    df = pd.read_csv(csv_file, parse_dates=['date'])

    start_date = df['date'].min().strftime('%Y-%m-%d')
    end_date = datetime.now().strftime("%Y-%m-%d")

    tickers = df['ticker'].unique().tolist()
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data.index = pd.to_datetime(data.index)  # 👈 This line fixes the type mismatch
    # Ensure we have today's row in the data
    today = pd.Timestamp(datetime.now().date())
    if today not in data.index:
        data.loc[today] = pd.Series([float('nan')] * len(data.columns), index=data.columns)

    # Make sure index stays datetime type
    data.index = pd.to_datetime(data.index)

    # Append real-time prices using .info for each ticker
    for ticker in tickers:
        try:
            ticker_obj = yf.Ticker(ticker)
            live_price = ticker_obj.info.get("regularMarketPrice")
            if live_price is not None:
                data.at[today, ticker] = live_price
        except Exception as e:
            print(f"Failed to fetch price for {ticker}: {e}")

    # Compute portfolio value over time
    portfolio_value = pd.Series(0.0, index=data.index)

    for _, row in df.iterrows():
        ticker = row['ticker']
        shares = row['shares']
        purchase_date = row['date']
        if ticker not in data.columns:
            continue
        mask = data.index >= purchase_date
        portfolio_value[mask] += data.loc[mask, ticker] * shares

    initial_value = (df['shares'] * df['buy_price']).sum()
    latest_value = portfolio_value.iloc[-1]
    growth = 100.0 * (latest_value - initial_value) / initial_value

    days_held = (datetime.now() - df['date'].min()).days
    years_held = days_held / 365.0

    return portfolio_value, initial_value, latest_value, growth, years_held

