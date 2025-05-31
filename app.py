from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
from io import BytesIO
from my_stocks import get_portfolio_data

app = Flask(__name__)

@app.route("/")
def index():
    portfolio_value, initial_value, latest_value, growth, years_held = get_portfolio_data()
    return render_template("index.html",
                           current_value=round(latest_value, 2),
                           growth_percent=round(growth, 2))

@app.route("/plot.png")
def plot_png():
    portfolio_value, initial_value, latest_value, growth, years_held = get_portfolio_data()

    target_5 = initial_value * 1.05 * years_held
    #target_10 = initial_value * 1.10

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    portfolio_value.plot(ax=ax, label="Portfolio Value", linewidth=2)
    ax.axhline(y=target_5, color='red', linestyle='--', label='5% FD')
    #ax.axhline(y=target_10, color='blue', linestyle='--', label='Target +10%')
    ax.axhline(y=latest_value, color='cyan', linestyle='--', label=f'Growth: {growth:.2f}%')

    ax.set_title("TFSA Portfolio Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value (CAD)")
    ax.grid(True)
    ax.legend()

    # Convert plot to image
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run()

