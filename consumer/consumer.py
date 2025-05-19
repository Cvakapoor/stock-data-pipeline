import io
import json
import pandas as pd
from kafka import KafkaConsumer
from datetime import datetime
from zoneinfo import ZoneInfo
import boto3
from botocore.client import Config

# -------- Upload to MinIO --------
def upload_to_minio(df, bucket_name="processed"):
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url="http://minio:9000",
            aws_access_key_id="minio",
            aws_secret_access_key="minio123",
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        now = datetime.now(ZoneInfo("Europe/Oslo")).strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"stock_data_{now}.csv"

        s3.put_object(Bucket=bucket_name, Key=filename, Body=csv_buffer.getvalue())
        print(f"✅ Uploaded {filename} to MinIO bucket '{bucket_name}'")
    except Exception as e:
        print(f"❌ Failed to upload to MinIO: {e}")

# -------- Kafka Consumer --------
consumer = KafkaConsumer(
    "stock_prices",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="stock-group",
)

print("📥 Listening to Kafka topic 'stock_prices'...")

data_buffer = []

try:
    for message in consumer:
        record = message.value
        print(f"📩 Received: {record}")
        data_buffer.append(record)

        if len(data_buffer) >= 22:
            df = pd.DataFrame(data_buffer)
            upload_to_minio(df)
            data_buffer.clear()

except KeyboardInterrupt:
    print("\n🛑 Consumer interrupted by user.")

finally:
    if data_buffer:
        df = pd.DataFrame(data_buffer)
        upload_to_minio(df)
    print("👋 Consumer shut down cleanly.")