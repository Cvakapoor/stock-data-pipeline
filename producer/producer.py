print("🟢 Starting producer...")

from kafka import KafkaProducer
import json
import requests
import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo
import csv
import random

# Your Finnhub API key
FINNHUB_API_KEY = "YOUR_FINNHUB_API_KEY"
# Ensure you have the correct API key

# Kafka configuration
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda m: json.dumps(m).encode("utf-8")
)

# Load symbols
def load_symbols_from_csv(filename):
    symbols = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                symbols.append(row[0].strip())
    return symbols

symbols = load_symbols_from_csv("tickers.txt")

# Market hours check (Oslo time)
def is_market_open(now):
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    market_open = dt_time(15, 30)
    market_close = dt_time(22, 0)
    return market_open <= now.time() <= market_close

# Fetch real-time quote
def fetch_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# Build event from quote
def build_event(symbol):
    quote = fetch_quote(symbol)
    if quote and quote.get("c") is not None:
        event = {
            "symbol": symbol,
            "timestamp": datetime.now(ZoneInfo("Europe/Oslo")).isoformat(),
            "price": quote["c"],
            "high": quote.get("h"),
            "low": quote.get("l"),
            "prev_close": quote.get("pc")
        }
        return event
    else:
        print(f"⚠️ Skipping {symbol} due to missing data.")
        return None

# Main producer logic
def run_producer():
    now = datetime.now(ZoneInfo("Europe/Oslo"))
    if not is_market_open(now):
        print(f"🛑 Market is closed at {now.time()}. Skipping data fetch.")
        return

    print("🚀 Producing stock events")
    for symbol in symbols:
        try:
            event = build_event(symbol)
            if event:
                print(f"📤 Sending to Kafka: {event}")
                producer.send("stock_prices", event)
        except Exception as e:
            print(f"❌ Error for {symbol}: {e}")
        time.sleep(1.1 + random.random() * 0.3)  # avoid throttling

    producer.flush()
    print("✅ All events sent.")

if __name__ == "__main__":
    run_producer()
