import sys
import os
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.trigger_rule import TriggerRule  
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='kafka_pipeline_dag',
    default_args=default_args,
    description='Kafka Stock Pipeline with Volatility & Alerts',
    schedule='*/1 * * * *',
    start_date=datetime(2025, 5, 1, tzinfo=ZoneInfo("Europe/Oslo")),
    catchup=False,
) as dag:

    produce_task = DockerOperator(
        task_id='produce_stock_data',
        image='stock_pipeline-producer:latest',
        command='sh -c "python /app/producer.py"',
        auto_remove='success',
        docker_url='tcp://host.docker.internal:2375',
        network_mode='airflow_net',
        tty=True,
    )

    load_to_postgres_task = DockerOperator(
        task_id='load_minio_to_postgres',
        image='stock_pipeline-loader:latest',
        command='sh -c "python /app/load_minio_to_postgres.py"',
        auto_remove='success',
        docker_url='tcp://host.docker.internal:2375',
        network_mode='airflow_net',
        tty=True,
    )

    compute_volatility_task = DockerOperator(
        task_id='compute_volatility',
        image='stock_pipeline-volatility:latest',
        command='sh -c "python /app/compute_volatility.py"',
        auto_remove='success',
        docker_url='tcp://host.docker.internal:2375',
        network_mode='airflow_net',
        tty=True,
    )

    generate_alerts_task = DockerOperator(
        task_id='generate_stock_alerts',
        image='stock_pipeline-alerts:latest',
        command='sh -c "python /app/alerts.py"',
        auto_remove='success',
        docker_url='tcp://host.docker.internal:2375',
        network_mode='airflow_net',
        tty=True,
    )

    # ✅ Optional: Manual historical data loader task
    load_historical_task = DockerOperator(
        task_id='load_historical_data',
        image='stock_pipeline-historical-loader:latest',
        command='sh -c "python /app/load_historical.py"',
        auto_remove='success',
        docker_url='tcp://host.docker.internal:2375',
        network_mode='airflow_net',
        tty=True,
        trigger_rule=TriggerRule.ALL_SUCCESS  # Will run only if explicitly triggered or added to a sequence
    )

    # 🔁 DAG task order for real-time pipeline
    produce_task >> load_to_postgres_task >> compute_volatility_task >> generate_alerts_task

    # ❌ Do not chain load_historical_task unless you want it to run regularly
