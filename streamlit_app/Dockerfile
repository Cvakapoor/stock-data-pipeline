FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app code
COPY . /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Wait for PostgreSQL before starting Streamlit
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose default Streamlit port
EXPOSE 8501

# Start the Streamlit app after confirming PostgreSQL is ready
CMD ["/wait-for-it.sh", "postgres:5432", "-t", "60", "--", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]