from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import requests
import logging

app = Flask(__name__)
API_KEY = "6205859ea1cd82.12555535"

# Protokollierung konfigurieren
logging.basicConfig(level=logging.INFO)

def fetch_stock_data(symbol):
    logging.info(f'Fetching data for {symbol}')
    url = f'https://eodhistoricaldata.com/api/eod/{symbol}.US?api_token={API_KEY}&order=d'
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f'Error fetching data: {response.status_code}')
        return pd.DataFrame()
    data = response.json()
    df = pd.DataFrame(data)
    if df.empty:
        logging.warning(f'No data returned for {symbol}')
        return df
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

def create_plot(df1, df2, symbol1, symbol2):
    fig = px.line()
    if not df1.empty:
        fig.add_scatter(x=df1.index, y=df1['close'], mode='lines', name=symbol1)
    if not df2.empty:
        fig.add_scatter(x=df2.index, y=df2['close'], mode='lines', name=symbol2)
    return pio.to_json(fig)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    symbol1 = request.form.get('symbol1').upper()
    symbol2 = request.form.get('symbol2').upper()
    
    df1 = fetch_stock_data(symbol1)
    df2 = fetch_stock_data(symbol2)
    
    plot_json = create_plot(df1, df2, symbol1, symbol2)
    
    return jsonify(plot_json)

if __name__ == '__main__':
    app.run(debug=True)
