import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Stock Dashboard", layout="wide")
OSLO_TZ = ZoneInfo("Europe/Oslo")

# --- Sidebar ---
st.sidebar.title("📊 Stock Dashboard")

# Load available tickers from PostgreSQL
@st.cache_data
def get_available_tickers():
    conn = psycopg2.connect(
        dbname='airflow',
        user='airflow',
        password='airflow',
        host='postgres',
        port='5432'
    )
    df = pd.read_sql("SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol;", conn)
    conn.close()
    return df['symbol'].tolist()

tickers = get_available_tickers()

if not tickers:
    st.warning("No ticker data found in the database.")
    st.stop()

ticker = st.sidebar.selectbox("Select Ticker", tickers)

# --- Load data ---
@st.cache_data
def load_data(ticker):
    conn = psycopg2.connect(
        dbname='airflow',
        user='airflow',
        password='airflow',
        host='postgres',
        port='5432'
    )

    price_query = """
        SELECT timestamp, price
        FROM stock_prices
        WHERE symbol = %s
        ORDER BY timestamp;
    """
    volatility_query = """
        SELECT timestamp, volatility, rolling_mean, return_pct, sharpe_ratio
        FROM stock_volatility
        WHERE symbol = %s
        ORDER BY timestamp;
    """
    alerts_query = """
        SELECT alert_time as timestamp, alert_message as message
        FROM stock_alerts
        WHERE symbol = %s
        ORDER BY alert_time DESC
        LIMIT 10;
    """

    df_price = pd.read_sql(price_query, conn, params=(ticker,))
    df_vol = pd.read_sql(volatility_query, conn, params=(ticker,))
    df_alerts = pd.read_sql(alerts_query, conn, params=(ticker,))
    conn.close()

    # Convert timestamps
    df_price['timestamp'] = pd.to_datetime(df_price['timestamp'], utc=True).dt.tz_convert(OSLO_TZ)
    df_vol['timestamp'] = pd.to_datetime(df_vol['timestamp'], utc=True).dt.tz_convert(OSLO_TZ)
    df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'], utc=True).dt.tz_convert(OSLO_TZ)

    return df_price, df_vol, df_alerts

df_price, df_vol, df_alerts = load_data(ticker)

# --- Price Chart ---
st.header(f"📈 Price: {ticker}")
fig_price = px.line(df_price, x='timestamp', y='price', title='Price Over Time')
st.plotly_chart(fig_price, use_container_width=True)

# --- Volatility Charts ---
st.header("🌪️ Volatility Metrics")
col1, col2 = st.columns(2)

with col1:
    fig_vol = px.line(df_vol, x='timestamp', y='volatility', title='Volatility Over Time')
    st.plotly_chart(fig_vol, use_container_width=True)

with col2:
    fig_sharpe = px.line(df_vol, x='timestamp', y='sharpe_ratio', title='Sharpe Ratio Over Time')
    st.plotly_chart(fig_sharpe, use_container_width=True)

# --- Alerts ---
st.header("⚠️ Risk Alerts")
if df_alerts.empty:
    st.info("No alerts triggered yet.")
else:
    df_alerts['timestamp'] = df_alerts['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    st.table(df_alerts[['timestamp', 'message']])
