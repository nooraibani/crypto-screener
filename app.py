import streamlit as st
import pandas as pd
import requests

# ============================================================
# Page Config
# ============================================================
st.set_page_config(page_title="Crypto Screener", layout="wide")
st.title("📊 Crypto Screener")

# Binance Public API (Block से बचने के लिए)
BASE_URL = "https://data-api.binance.vision/api/v3"

# ============================================================
# Functions
# ============================================================
@st.cache_data(ttl=300)
def get_binance_data():
    response = requests.get(f"{BASE_URL}/ticker/24hr")
    data = response.json()
    usdt_data = [d for d in data if d['symbol'].endswith('USDT')]
    return usdt_data

def get_klines(symbol, interval, limit):
    url = f"{BASE_URL}/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        res = requests.get(url).json()
        if len(res) > 0:
            return float(res[0][1])
    except:
        pass
    return None

# ============================================================
# Main App
# ============================================================
with st.spinner('Binance से डेटा लाया जा रहा है... (1-2 मिनट)'):
    ticker_data = get_binance_data()

results = []
progress_bar = st.progress(0)

timeframes = {'1h': '1h', '8h': '8h', '1d': '1d', '7d': '1d', '15d': '1d', '30d': '1d', '45d': '1d', '60d': '1d'}
limits = {'1h': 1, '8h': 8, '1d': 1, '7d': 7, '15d': 15, '30d': 30, '45d': 45, '60d': 60}

total_coins = len(ticker_data)

for i, coin in enumerate(ticker_data):
    symbol = coin['symbol']
    price = float(coin['lastPrice'])
    volume = float(coin['quoteVolume'])
    
    if volume < 1000000:
        continue
        
    row = {
        'Symbol': symbol.replace('USDT', ''),
        'Price': price,
        'Volume ($M)': round(volume / 1000000, 2),
    }
    
    for tf_name, tf_interval in timeframes.items():
        limit = limits[tf_name] + 1
        past_price = get_klines(symbol, tf_interval, limit)
        if past_price and past_price > 0:
            change = ((price / past_price) - 1) * 100
            row[f'{tf_name} %'] = round(change, 2)
        else:
            row[f'{tf_name} %'] = None
            
    results.append(row)
    
    if i % 10 == 0:
        progress_bar.progress((i + 1) / total_coins)

progress_bar.empty()

df = pd.DataFrame(results)

if '30d %' in df.columns:
    df = df.sort_values('30d %', ascending=False)

st.write("### 📈 Live Data")
st.dataframe(df, use_container_width=True, hide_index=True)
