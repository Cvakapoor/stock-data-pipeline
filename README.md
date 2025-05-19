# 📈 Real-Time Stock Volatility Monitoring Pipeline

This project implements a **real-time stock analytics pipeline** that streams live and simulated stock prices, computes volatility metrics, generates alerts, and visualizes data. It uses a modern stack including **Kafka, PostgreSQL, MinIO, Airflow**, and **Streamlit**.

---

## 🚀 Features

- 🔄 **Real-Time Stock Price Ingestion** from Finnhub

- 📥 **Streaming via Kafka** for high-throughput processing

- 💾 **MinIO as Data Lake** for raw CSV storage

- 🐘 **PostgreSQL** for structured analytical queries

- 📊 **Volatility Analytics** with Sharpe Ratio, Log Returns, etc.

- ⚠️ **Alerting System** for price drops and abnormal volatility

- 📅 **Orchestration with Airflow** (runs every minute)

- 📺 **Streamlit Dashboard** for real-time insights

---

## 🛠️ Technologies Used

| Component     | Tool                   |
| ------------- | ---------------------- |
| Orchestration | Apache Airflow         |
| Messaging     | Apache Kafka           |
| Storage       | PostgreSQL, MinIO      |
| Programming   | Python, Pandas, NumPy  |
| Visualization | Streamlit              |
| Deployment    | Docker, Docker Compose |

---

## 🧱 Architecture Overview

```mermaid
%%{init: {'themeVariables': { 'primaryColor': '#f9f', 'edgeLabelBackground':'#eee', 'clusterBkg': '#ddf'}}}%%
graph TD
    classDef source fill:#f9f,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef kafka fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef airflow fill:#90caf9,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef storage fill:#a5d6a7,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef dashboard fill:#ffccbc,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;

    subgraph Data Sources
        direction TB
        A1[Finnhub API - Real-time]:::source
        A2[Simulated Data Generator]:::source
    end

    subgraph Kafka
        direction TB
        B1[Producer]:::kafka
        B2[Consumer]:::kafka
    end

    subgraph Airflow
        direction TB
        C1[Producer DAG]:::airflow
        C2[Load MinIO to PostgreSQL DAG]:::airflow
        C3[Volatility Calculation DAG]:::airflow
        C4[Alerts DAG]:::airflow
        C5[Simulated Data Loader DAG]:::airflow
    end

    subgraph Storage
        direction TB
        D1[MinIO - Raw CSV Storage]:::storage
        D2[PostgreSQL - Processed Data]:::storage
    end

    subgraph Dashboard
        direction TB
        E1[Streamlit Dashboard]:::dashboard
    end

    A1 --> B1
    A2 --> C5
    B1 --> B2
    B2 --> D1
    D1 --> C2
    C2 --> D2
    C3 --> D2
    C4 --> D2
    C5 --> D2
    D2 --> E1
```

---

## ⚙️ Setup Instructions

- ⏰ **Clone the Repository**
<pre> git clone https://github.com/cvakapoor/stock-volatility-pipeline.git</pre>
<pre> cd stock-volatility-pipeline</pre>
  
- ⏰ **Run PostgreSQL and Airflow**

You can either:

1. Run PostgreSQL and Airflow in separate containers manually, or
2. Integrate both into a unified `docker-compose.yml` setup.

Make sure to update your `docker-compose.yml` accordingly, and drop/recreate the Docker network if needed.

📌 **Note:** Ensure that the Airflow and PostgreSQL services are connected via the same Docker network.

---

## 📊 Streamlit Dashboard

The project includes an interactive **Streamlit dashboard** (streamlit_app.py) to visualize real-time stock metrics, including:

- 📈 **Price Trends** — Line chart of price over time
  
- 🌪️ **Volatility Metrics** — Visuals for volatility and Sharpe ratio
  
- ⚠️ **Recent Alerts** — Table of triggered alert messages
  
