# 📈 Real-Time Stock Volatility Monitoring Pipeline

This project implements a real-time stock analytics pipeline that streams live and simulated stock prices, computes volatility metrics, generates alerts, and visualizes data. It uses a modern stack including Kafka, PostgreSQL, MinIO, Airflow, and Streamlit.

---

## 🚀 Features

- ⏰ **Scheduled Data Ingestion**: Fetches stock price data from an external API every minute using Apache Airflow.
- 🧮 **Volatility Computation**: Calculates rolling volatility, returns, and Sharpe ratio using pandas.
- ⚠️ **Anomaly Detection**: Detects significant volatility spikes and logs risk alerts.
- 🗃️ **Storage in PostgreSQL**: All data and alerts are stored in a PostgreSQL database for durability and queryability.
- 📊 **Streamlit Dashboard**: Interactive UI to visualize metrics and track recent alerts.

---

## 🛠️ Technologies Used

- **Apache Airflow** – Workflow orchestration and scheduling
- **PostgreSQL** – Relational database for storing price, volatility, and alert data
- **Streamlit** – Web dashboard for data visualization
- **Docker & Docker Compose** – Containerization and orchestration
- **Pandas / Plotly** – Data processing and charting
- **psycopg2** – PostgreSQL database connector for Python

---

## 🧱 Architecture Overview

```plaintext
          +------------------------+
          |    Stock API Source    |
          +-----------+------------+
                      |
                      ▼
         +------------+------------+
         |     Airflow DAGs        |
         |  (price fetch & alerts) |
         +------------+------------+
                      |
                      ▼
            +---------+---------+
            |     PostgreSQL    |
            |  stock_prices     |
            |  stock_volatility |
            |  stock_alerts     |
            +---------+---------+
                      |
                      ▼
           +----------+----------+
           |     Streamlit UI     |
           |  Interactive Charts  |
           +----------------------+
