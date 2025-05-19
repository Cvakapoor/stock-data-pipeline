import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np

def load_base_prices_from_file(filename="simulate.txt"):
    return pd.read_csv(filename)

def simulate_intraday_data(base_row, from_dt, to_dt, interval_minutes=1):
    timestamps = pd.date_range(from_dt, to_dt, freq=f"{interval_minutes}min", tz=ZoneInfo("Europe/Oslo"))
    n = len(timestamps)

    base_price = base_row["price"]
    high_base = base_row["high"]
    low_base = base_row["low"]
    prev_close = base_row["prev_close"]
    symbol = base_row["symbol"]

    # Generate noise to simulate a price walk
    drift = np.random.normal(0, 0.05, size=n).cumsum()
    prices = base_price + drift

    # Simulate highs/lows around each price point
    highs = prices + np.random.uniform(0.1, 0.5, size=n)
    lows = prices - np.random.uniform(0.1, 0.5, size=n)

    return pd.DataFrame({
        "symbol": symbol,
        "timestamp": timestamps,
        "price": prices,
        "high": highs,
        "low": lows,
        "prev_close": [prev_close] * n
    })

def simulate_for_multiple_days(base_row, start_date, end_date):
    all_days_data = []

    current_date = start_date
    while current_date <= end_date:
        from_dt = datetime(current_date.year, current_date.month, current_date.day, 15, 30, tzinfo=ZoneInfo("Europe/Oslo"))
        to_dt = datetime(current_date.year, current_date.month, current_date.day, 22, 0, tzinfo=ZoneInfo("Europe/Oslo"))
        
        day_data = simulate_intraday_data(base_row, from_dt, to_dt)
        all_days_data.append(day_data)
        
        current_date += timedelta(days=1)

    return pd.concat(all_days_data, ignore_index=True)

def insert_into_postgres(df, conn):
    if df.empty:
        return

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            symbol TEXT,
            timestamp TIMESTAMPTZ,
            price FLOAT,
            high FLOAT,
            low FLOAT,
            prev_close FLOAT
        );
    """)
    conn.commit()

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO stock_prices (symbol, timestamp, price, high, low, prev_close)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (
            row["symbol"],
            row["timestamp"],
            row["price"],
            row["high"],
            row["low"],
            row["prev_close"]
        ))
    conn.commit()
    cur.close()
    print(f"✅ Inserted {len(df)} rows for {df.iloc[0]['symbol']}.")

if __name__ == "__main__":
    start_date = datetime(2025, 5, 12).date()
    end_date = datetime(2025, 5, 16).date()

    base_df = load_base_prices_from_file("simulate.txt")

    conn = psycopg2.connect(
        dbname='airflow',
        user='airflow',
        password='airflow',
        host='postgres',
        port='5432'
    )

    for _, row in base_df.iterrows():
        df = simulate_for_multiple_days(row, start_date, end_date)
        insert_into_postgres(df, conn)

    conn.close()
