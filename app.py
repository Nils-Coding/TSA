from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import requests
import logging
import config

app = Flask(__name__)
API_KEY = config.EODHD_API_KEY

# Protokollierung konfigurieren
logging.basicConfig(level=logging.INFO)

def fetch_stock_data(symbol, start_date=None, end_date=None):
    logging.info(f'Fetching data for {symbol}')
    url = f'https://eodhistoricaldata.com/api/eod/{symbol}.US?api_token={API_KEY}&order=d&fmt=json'
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
    df = df[['close']]
    
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]
    return df

def create_plot(df1, df2, symbol1, symbol2):
    yaxis_title = "Closing Price (USD)"
    plot_title = f"Closing Prices of {symbol1} and {symbol2}"
    
    fig = px.line()
    if not df1.empty:
        fig.add_scatter(x=df1.index, y=df1['close'], mode='lines', name=symbol1)
    if not df2.empty:
        fig.add_scatter(x=df2.index, y=df2['close'], mode='lines', name=symbol2)
    fig.update_layout(
        title=plot_title,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        template="plotly_dark",
        font=dict(size=14),
        title_font=dict(size=24, color='#ffffff'),
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='#ffffff',
            linewidth=2,
            ticks='outside',
            tickfont=dict(size=14, color='#ffffff')
        ),
        yaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='#ffffff',
            linewidth=2,
            ticks='outside',
            tickfont=dict(size=14, color='#ffffff')
        ),
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
    )

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

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    #print(df1)
    #print(df2)
    #print(start_date)
    #print(end_date)

    if start_date == "":
        start_date = max(df1.index.min(), df2.index.min())
        
    df1 = df1[df1.index >= start_date]
    df2 = df2[df2.index >= start_date]
    
    if end_date != "":

        df1 = df1[df1.index <= end_date]
        df2 = df2[df2.index <= end_date]
    
    if df1.empty or df2.empty:
        return "One or both symbols returned no data", 400
    
    plot_json = create_plot(df1, df2, symbol1, symbol2)
    
    return plot_json

if __name__ == '__main__':
    app.run(debug=True)
    #df1 = fetch_stock_data("AAPL")
    #df2 = fetch_stock_data("AMZN")
    #plot_json = create_plot(df1, df2, "AAPL", "AMZN")
    #print(plot_json)
    #print(df.head())
    #print(df.tail())
    #print(df.info())


