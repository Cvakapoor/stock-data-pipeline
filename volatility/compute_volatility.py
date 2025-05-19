import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

def compute_volatility_metrics():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname='airflow',
        user='airflow',
        password='airflow',
        host='postgres',
        port='5432'
    )
    cur = conn.cursor()

    # Create table with primary key to avoid duplicates
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_volatility (
            symbol TEXT,
            timestamp TIMESTAMPTZ,
            volatility FLOAT,
            rolling_mean FLOAT,
            return_pct FLOAT,
            sharpe_ratio FLOAT,
            PRIMARY KEY (symbol, timestamp)
        );
    """)
    conn.commit()

    # Load stock prices
    query = """
        SELECT symbol, price, timestamp
        FROM stock_prices
        ORDER BY timestamp ASC;
    """
    df = pd.read_sql(query, conn)

    if df.empty:
        print("⚠️ No data available in stock_prices.")
        cur.close()
        conn.close()
        return

    # Ensure timestamp is timezone-aware and localized
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert(ZoneInfo("Europe/Oslo"))
    df.set_index('timestamp', inplace=True)

    results = []

    for symbol, group in df.groupby('symbol'):
        # Resample to 1-minute frequency, forward fill missing prices
        group = group.resample('1min').apply(lambda df: df.select_dtypes(include='number').mean()).ffill()

        # Calculate log returns for 15-minute interval
        group['log_return'] = np.log(group['price'] / group['price'].shift(15))

        # Calculate rolling volatility (std dev of log returns) over last 5 intervals
        group['volatility'] = group['log_return'].rolling(window=5).std()

        # Annualize volatility (assume 252 trading days * 390 minutes per trading day)
        annualization_factor = np.sqrt(252 * 390)
        group['volatility'] = group['volatility'] * annualization_factor

        # Rolling mean price over last 5 intervals
        group['rolling_mean'] = group['price'].rolling(window=5).mean()

        # Cumulative log return over last 15 intervals, then convert to pct return
        group['return_pct'] = np.exp(group['log_return'].rolling(window=15).sum()) - 1

        # Sharpe ratio: mean return over volatility (add small epsilon to avoid div by zero)
        eps = 1e-9
        mean_return = group['return_pct'].rolling(window=5).mean()
        group['sharpe_ratio'] = mean_return / (group['volatility'] + eps)

        # Drop rows with NaNs to find latest complete row
        latest = group.dropna().iloc[-1:]

        if not latest.empty:
            vol = latest['volatility'].values[0]
            ret = latest['return_pct'].values[0]
            sharpe = latest['sharpe_ratio'].values[0]

            print(f"Symbol: {symbol}, Volatility: {vol:.6f}, Return: {ret:.6%}, Sharpe: {sharpe:.6f}")

            results.append({
                'symbol': symbol,
                'timestamp': latest.index[0],
                'volatility': vol,
                'rolling_mean': latest['rolling_mean'].values[0],
                'return_pct': ret,
                'sharpe_ratio': sharpe
            })

    if not results:
        print("⚠️ No complete data to insert.")
        cur.close()
        conn.close()
        return

    result_df = pd.DataFrame(results)

    for _, row in result_df.iterrows():
        cur.execute("""
            INSERT INTO stock_volatility (symbol, timestamp, volatility, rolling_mean, return_pct, sharpe_ratio)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, timestamp) DO NOTHING;
        """, (
            row['symbol'],
            row['timestamp'],
            row['volatility'],
            row['rolling_mean'],
            row['return_pct'],
            row['sharpe_ratio']
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Inserted {len(result_df)} volatility row(s).")

if __name__ == "__main__":
    compute_volatility_metrics()
