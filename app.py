import yfinance as yf
import numpy as np
import pandas as pd
from qiskit import QuantumCircuit, transpile
from qiskit.providers.basic_provider import BasicSimulator
from flask import Flask, request, jsonify, render_template, url_for, redirect, session
import plotly.express as px
import plotly.io as pio
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
CONNECTION_STRING = "mongodb://var:XekE2utWabCRCXfUhd4rMU0FeYvopJeopKpCjFKSDylUzSbddVKU71Dp9zVAlcQEkPltwI7wDGF6ACDbgftmSw==@var.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@var@"
DB_NAME = "userdata"
COLLECTION_NAME = "users"

# Initialize MongoDB client
try:
    client = MongoClient(CONNECTION_STRING)
    try:
        client.server_info()  # Validate connection string
    except (pymongo.errors.OperationFailure, pymongo.errors.ConnectionFailure, pymongo.errors.ExecutionTimeout) as err:
        sys.exit("Can't connect: " + str(err))
except Exception as err:
    sys.exit("Error: " + str(err))

db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def get_historical_data(stock_name):
    stock = yf.Ticker(stock_name)
    hist = stock.history(period="1y")  
    hist['Returns'] = hist['Close'].pct_change() 
    return hist.dropna()


def quantum_random_number_generator(n_qubits):
    qrng_circuit = QuantumCircuit(n_qubits, n_qubits)
    qrng_circuit.h(range(n_qubits))
    qrng_circuit.measure(range(n_qubits), range(n_qubits))
    sim_backend = BasicSimulator()
    job = sim_backend.run(transpile(qrng_circuit, sim_backend), shots=1)
    result = job.result()
    counts = result.get_counts()
    return int(list(counts.keys())[0], 2)

def monte_carlo_var(stock_name, investment_amount_usd, num_simulations=10000):
    historical_data = get_historical_data(stock_name)
    historical_returns = historical_data['Returns']
    
    if historical_returns.empty:
        return None, None, None

    simulated_returns = []
    for _ in range(num_simulations):
        quantum_seed = quantum_random_number_generator(10)
        np.random.seed(quantum_seed)
        simulated_returns.append(np.mean(np.random.choice(historical_returns, len(historical_returns))))
    
    var_95 = np.percentile(simulated_returns, 5)
    var_95_amount_usd = float(investment_amount_usd) * var_95  
    
    return var_95, var_95_amount_usd, historical_data


def generate_visualizations(stock_name, historical_data):
    if not os.path.exists('static'):
        os.makedirs('static')
    

    fig_box = px.box(historical_data, x='Returns', title=f'Box Plot of Daily Returns for {stock_name}')
    boxplot_path = 'static/boxplot.html'
    pio.write_html(fig_box, file=boxplot_path, auto_open=False)
    

    fig_close = px.line(historical_data, x=historical_data.index, y='Close', title=f'Closing Price of {stock_name} Over Time')
    closing_price_path = 'static/closing_price.html'
    pio.write_html(fig_close, file=closing_price_path, auto_open=False)
    

    fig_hist = px.histogram(historical_data, x='Returns', title=f'Histogram of Daily Returns for {stock_name}')
    hist_path = 'static/histogram.html'
    pio.write_html(fig_hist, file=hist_path, auto_open=False)


    fig_volume = px.line(historical_data, x=historical_data.index, y='Volume', title=f'Volume Traded Over Time for {stock_name}')
    volume_path = 'static/volume.html'
    pio.write_html(fig_volume, file=volume_path, auto_open=False)


    fig_candlestick = px.line(historical_data, x=historical_data.index, y=['High', 'Low', 'Open', 'Close'], title=f'Daily High-Low Price Range for {stock_name}', 
                              labels={'value': 'Price', 'variable': 'Price Type'}, 
                              template='plotly_white')
    candlestick_path = 'static/candlestick.html'
    pio.write_html(fig_candlestick, file=candlestick_path, auto_open=False)


    historical_data['50-day MA'] = historical_data['Close'].rolling(window=50).mean()
    historical_data['200-day MA'] = historical_data['Close'].rolling(window=200).mean()
    fig_ma = px.line(historical_data, x=historical_data.index, y=['Close', '50-day MA', '200-day MA'], 
                     title=f'Moving Averages for {stock_name}')
    ma_path = 'static/moving_averages.html'
    pio.write_html(fig_ma, file=ma_path, auto_open=False)

    delta = historical_data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    fig_rsi = px.line(RSI, x=RSI.index, y=RSI.values, title=f'Relative Strength Index (RSI) for {stock_name}')
    rsi_path = 'static/rsi.html'
    pio.write_html(fig_rsi, file=rsi_path, auto_open=False)


    exp12 = historical_data['Close'].ewm(span=12, adjust=False).mean()
    exp26 = historical_data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    fig_macd = px.line(macd, x=macd.index, y=macd.values, title=f'MACD for {stock_name}')
    fig_macd.add_scatter(x=signal.index, y=signal.values, mode='lines', name='Signal')
    macd_path = 'static/macd.html'
    pio.write_html(fig_macd, file=macd_path, auto_open=False)

    return boxplot_path, closing_price_path, hist_path, volume_path, candlestick_path, ma_path, rsi_path, macd_path

app = Flask(__name__)
app.secret_key = 'QuantumVaR'
@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    user = collection.find_one({'email': email, 'password': password})
    if user:
        session['username'] = user['user']
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error='Invalid email or password')

@app.route('/signup', methods=['POST'])
def signup_user():
    email = request.form['email']
    password = request.form['password']
    user = request.form['username']
    existing_user = collection.find_one({'email': email})
    if existing_user:
        return render_template('login.html', error='User already exists')
    else:
        collection.insert_one({'email': email, 'password': password, 'user': user})
        return render_template('login.html', success='User created successfully')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/calculate_var', methods=['POST'])
def calculate_var():
    data = request.json
    stock_name = data.get('stock_name')
    investment_amount_usd = float(data.get('investment_amount', 1))  
    var_95, var_95_amount_usd, historical_data = monte_carlo_var(stock_name, investment_amount_usd)
    
    if var_95 is None:
        return jsonify({'error': 'Invalid stock name or no data available'}), 400
    

    boxplot_path, closing_price_path, hist_path, volume_path, candlestick_path, ma_path, rsi_path, macd_path = generate_visualizations(stock_name, historical_data)
    
    return jsonify({
        'stock_name': stock_name,
        'investment_amount': investment_amount_usd,
        'VaR_95': var_95,
        'VaR_95_amount_usd': var_95_amount_usd,
        'boxplot_url': boxplot_path,
        'closing_price_url': closing_price_path,
        'histogram_url': hist_path,
        'volume_traded_url': volume_path,
        'candlestick_chart_url': candlestick_path,
        'moving_averages_url': ma_path,
        'rsi_url': rsi_path,
        'macd_url': macd_path
    })

if __name__ == '__main__':
    app.run(port=5050, debug=True)