from flask import Flask, render_template, request, redirect, url_for
import requests
import pygal
from pygal.style import DarkSolarizedStyle
from datetime import datetime

app = Flask(__name__)

API_KEY = '5EW2VPXRG7XF7PWK'

# Function to fetch stock data from Alpha Vantage
def get_stock_data(symbol, function, api_key, start_date, end_date):
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&datatype=json'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if 'Error Message' in data or not data:
        return None
    time_series_key = list(data.keys())[-1]
    stock_data = data.get(time_series_key, {})
    return {date: value for date, value in stock_data.items() if start_date <= date <= end_date}

# Function to create a chart
def create_chart(data, title, chart_type):
    chart = pygal.Line(style=DarkSolarizedStyle) if chart_type == 'Line' else pygal.Bar(style=DarkSolarizedStyle)
    chart.title = title
    chart.x_labels = list(data.keys())
    open_prices = [float(info['1. open']) for info in data.values()]
    high_prices = [float(info['2. high']) for info in data.values()]
    low_prices = [float(info['3. low']) for info in data.values()]
    close_prices = [float(info['4. close']) for info in data.values()]
    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)
    return chart.render_data_uri()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        chart_type = request.form.get("chart_type")
        function = request.form.get("function")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        stock_data = get_stock_data(symbol, function, API_KEY, start_date, end_date)
        if stock_data:
            chart_uri = create_chart(stock_data, f"{symbol} Stock Prices", chart_type)
            return render_template("index.html", chart_uri=chart_uri, symbol=symbol)
        else:
            error = "No data available for the selected range or symbol."
            return render_template("index.html", error=error)

    # Load stock symbols here (either from an API or local CSV file)
    symbols = ["AAPL", "MSFT", "GOOGL"]  # Example; replace with dynamic loading
    return render_template("index.html", symbols=symbols)

if __name__ == "__main__":
    app.run(debug=True)
