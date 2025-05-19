import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo

# Alert thresholds
PRICE_DROP_THRESHOLD = 0.05  # 5% drop
VOLATILITY_SPIKE = 0.02
OSLO_TZ = ZoneInfo("Europe/Oslo")

def create_alerts_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_alerts (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            alert_time TIMESTAMPTZ,
            alert_message TEXT
        );
    """)

def fetch_latest_data(conn):
    with conn.cursor() as cur:
        # Latest price per symbol
        cur.execute("""
            SELECT DISTINCT ON (symbol) symbol, price, timestamp
            FROM stock_prices
            ORDER BY symbol, timestamp DESC;
        """)
        latest_prices = cur.fetchall()

        # Latest volatility per symbol
        cur.execute("""
            SELECT DISTINCT ON (symbol) symbol, volatility
            FROM stock_volatility
            ORDER BY symbol, timestamp DESC;
        """)
        latest_volatility = {row[0]: row[1] for row in cur.fetchall()}

    return latest_prices, latest_volatility

def fetch_previous_price(conn, symbol, current_timestamp):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT price FROM stock_prices
            WHERE symbol = %s AND timestamp < %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (symbol, current_timestamp))
        res = cur.fetchone()
        return res[0] if res else None

def check_alerts(latest_prices, latest_volatility, conn):
    alerts = []
    for symbol, price, timestamp in latest_prices:
        prev_price = fetch_previous_price(conn, symbol, timestamp)
        vol = latest_volatility.get(symbol)

        if prev_price:
            price_drop = (prev_price - price) / prev_price
            if price_drop >= PRICE_DROP_THRESHOLD:
                alerts.append((symbol, f"🔻 Price dropped {price_drop*100:.2f}% (from {prev_price:.2f} to {price:.2f})"))

        if vol is not None and vol > VOLATILITY_SPIKE:
            alerts.append((symbol, f"🚨 Volatility spiked to {vol:.4f}"))

    return alerts

def save_alerts(conn, alerts):
    if not alerts:
        return

    with conn.cursor() as cur:
        now = datetime.now(OSLO_TZ)
        for symbol, message in alerts:
            cur.execute("""
                INSERT INTO stock_alerts (symbol, alert_time, alert_message)
                VALUES (%s, %s, %s);
            """, (symbol, now, message))
        conn.commit()

def main():
    try:
        conn = psycopg2.connect(
            dbname='airflow',
            user='airflow',
            password='airflow',
            host='postgres',
            port='5432'
        )

        # Always ensure the alerts table exists
        with conn.cursor() as cur:
            create_alerts_table(cur)
        conn.commit()

        latest_prices, latest_volatility = fetch_latest_data(conn)
        alerts = check_alerts(latest_prices, latest_volatility, conn)

        now_str = datetime.now(OSLO_TZ).isoformat()
        if alerts:
            print(f"🕒 Alerts at {now_str}:")
            for symbol, message in alerts:
                print(f"⚠️ {symbol}: {message}")
            save_alerts(conn, alerts)
        else:
            print(f"🕒 No alerts at {now_str}.")

    except Exception as e:
        print(f"❌ Alert system failed: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
