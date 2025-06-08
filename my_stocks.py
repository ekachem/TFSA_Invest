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
    data.index = pd.to_datetime(data.index)

    # Ensure today's row is present
    today = pd.Timestamp(datetime.now().date())
    if today not in data.index:
        data.loc[today] = pd.Series([float('nan')] * len(data.columns), index=data.columns)
    data.index = pd.to_datetime(data.index)

    # Append live prices
    for ticker in tickers:
        try:
            ticker_obj = yf.Ticker(ticker)
            live_price = ticker_obj.info.get("regularMarketPrice")
            if live_price is not None:
                data.at[today, ticker] = live_price
        except Exception as e:
            print(f"Failed to fetch price for {ticker}: {e}")

    # Build portfolio value over time
    portfolio_value = pd.Series(0.0, index=data.index)
    initial_value_series = pd.Series(0.0, index=data.index)

    for _, row in df.iterrows():
        ticker = row['ticker']
        shares = row['shares']
        buy_price = row['buy_price']
        purchase_date = row['date']

        if ticker not in data.columns:
            continue

        mask = data.index >= purchase_date
        portfolio_value[mask] += data.loc[mask, ticker] * shares
        initial_value_series[mask] += shares * buy_price

    # Calculate % growth over time
    growth_series = 100.0 * (portfolio_value - initial_value_series) / initial_value_series

    # Current values
    latest_value = portfolio_value.iloc[-1]
    initial_value = initial_value_series.iloc[-1]
    growth = growth_series.iloc[-1]

    days_held = (datetime.now() - df['date'].min()).days
    years_held = days_held / 365.0

    # --- Compute daily investment fraction ---
    daily_investment = df.copy()
    daily_investment['amount'] = daily_investment['shares'] * daily_investment['buy_price']
    daily_investment = daily_investment.groupby('date')['amount'].sum()

    total_investment = daily_investment.sum()
    investment_fraction = daily_investment / total_investment

    investment_series = pd.Series(0.0, index=portfolio_value.index)
    for date, frac in investment_fraction.items():
        if date in investment_series.index:
            investment_series.at[date] = frac

    max_growth = growth_series.max()
    investment_scaled = investment_series * (max_growth / investment_series.max())
    # --- Compute daily fixed deposit-style target growth ---
    start_date = growth_series.index.min()
    days = (growth_series.index - start_date).days
    target_growth_series = pd.Series((5.0 / 365.0) * days, index=growth_series.index)


    #return growth_series, initial_value, latest_value, growth, years_held
    #return growth_series, initial_value, latest_value, growth, years_held, investment_scaled
    return growth_series, initial_value, latest_value, growth, years_held, investment_scaled, target_growth_series


