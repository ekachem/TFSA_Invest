# app.py
from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
from io import BytesIO
from my_stocks import get_portfolio_data
import time

app = Flask(__name__)

# Global cache
portfolio_cache = {
    "timestamp": 0,
    "data": None
}

CACHE_DURATION = 10  # seconds

def get_cached_portfolio_data():
    current_time = time.time()
    if (current_time - portfolio_cache["timestamp"]) > CACHE_DURATION or portfolio_cache["data"] is None:
        portfolio_cache["data"] = get_portfolio_data()
        portfolio_cache["timestamp"] = current_time
    return portfolio_cache["data"]

@app.route("/")
def index():
    growth_series, initial_value, latest_value, growth, years_held, investment_scaled, target_growth_series = get_cached_portfolio_data()
    return render_template("index.html",
                           current_value=round(latest_value, 2),
                           growth_percent=round(growth, 2),
                           initial_value=round(initial_value, 2),
                           timestamp=int(time.time()))

@app.route("/plot.png")
def plot_png():
    growth_series, initial_value, latest_value, growth, years_held, investment_scaled, target_growth_series = get_cached_portfolio_data()


    target_growth = 5.0 * years_held  # expressed as %

    fig, ax = plt.subplots(figsize=(10, 5))
    growth_series.plot(ax=ax, label="Growth (%)", linewidth=2)
    ax.bar(investment_scaled.index, investment_scaled.values,
       width=1, alpha=0.3, color='orange', label='New Investment (scaled)')
    #ax.axhline(y=target_growth, color='red', linestyle='--', label='5% FD')
    target_growth_series.plot(ax=ax, color='red', linestyle='--', label='5% FD Target')
    ax.axhline(y=growth, color='cyan', linestyle='--', label=f'Growth: {growth:.2f}%')

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
