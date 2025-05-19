import io
import pandas as pd
import psycopg2
import boto3
from botocore.client import Config
from datetime import datetime
from zoneinfo import ZoneInfo

def load_and_archive():
    # Connect to MinIO
    s3 = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minio',
        aws_secret_access_key='minio123',
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    bucket = 'processed'
    archive_prefix = 'archive/'

    # List all files in 'processed' bucket
    response = s3.list_objects_v2(Bucket=bucket)
    if 'Contents' not in response:
        print("📂 No files to process.")
        return

    for obj in response['Contents']:
        key = obj['Key']
        if key.startswith(archive_prefix):
            continue  # Skip archived files

        print(f"📄 Processing file: {key}")

        # Read CSV from MinIO
        data = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(data['Body'].read()))

        # Parse and localize timestamps safely
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_convert(ZoneInfo("Europe/Oslo"))

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname='airflow',
            user='airflow',
            password='airflow',
            host='postgres',
            port='5432'
        )
        cur = conn.cursor()

        # Create table if not exists
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

        # Insert each row
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO stock_prices (
                    symbol, timestamp, price, high, low, prev_close
                ) VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                row.get('symbol'),
                row.get('timestamp'),
                row.get('price'),
                row.get('high'),
                row.get('low'),
                row.get('prev_close')
            ))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Inserted data from {key} into PostgreSQL")

        # Move processed file to archive
        archive_key = archive_prefix + key.split('/')[-1]
        s3.copy_object(Bucket=bucket, CopySource=f'{bucket}/{key}', Key=archive_key)
        s3.delete_object(Bucket=bucket, Key=key)
        print(f"📦 Moved {key} to {archive_key}")

if __name__ == "__main__":
    load_and_archive()