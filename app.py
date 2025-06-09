# app.py
from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
from io import BytesIO
from my_stocks import get_portfolio_data
import time

app = Flask(__name__)

portfolio_cache = {"timestamp": 0, "data": None}
CACHE_DURATION = 10

def get_cached_portfolio_data():
    current_time = time.time()
    if (current_time - portfolio_cache["timestamp"] > CACHE_DURATION) or portfolio_cache["data"] is None:
        portfolio_cache["data"] = get_portfolio_data()
        portfolio_cache["timestamp"] = current_time
    return portfolio_cache["data"]

@app.route("/")
def index():
    (growth_series, initial_value, latest_value, growth, years_held,
     investment_scaled, target_growth_series, upcoming_dividends,
     holdings, dividend_income, total_dividend_income, investment_history,
     sector_allocation, tfsa_limit, total_contributed, risk_flags) = get_cached_portfolio_data()

    return render_template("index.html",
                           current_value=round(latest_value, 2),
                           growth_percent=round(growth, 2),
                           initial_value=round(initial_value, 2),
                           timestamp=int(time.time()),
                           holdings=holdings,
                           upcoming_dividends=upcoming_dividends,
                           dividend_income=dividend_income,
                           total_dividend_income=round(total_dividend_income, 2),
                           investment_history=investment_history,
                           sector_allocation=sector_allocation,
                           tfsa_limit=round(tfsa_limit, 2),
                           total_contributed=round(total_contributed, 2),
                           risk_flags=risk_flags)

@app.route("/plot.png")
def plot_png():
    (growth_series, initial_value, latest_value, growth, years_held,
     investment_scaled, target_growth_series, *_rest) = get_cached_portfolio_data()

    fig, ax = plt.subplots(figsize=(10, 5))
    growth_series.plot(ax=ax, label="Growth (%)", linewidth=2)
    target_growth_series.plot(ax=ax, color='red', linestyle='--', label='5% FD Target')
    ax.bar(investment_scaled.index, investment_scaled.values, width=1,
           alpha=0.3, color='orange', label='Investment Activity (scaled)')

    ax.set_xlabel("Date")
    ax.set_title("TFSA Portfolio Growth Over Time")
    ax.set_ylabel("Growth (%)")
    ax.grid(True)
    ax.legend()

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run()
