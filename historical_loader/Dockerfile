FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all application files
COPY . /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: wait-for-it script if you want to delay until DB is ready
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Default command: run historical load script (can be overridden in DockerOperator)
CMD ["/wait-for-it.sh", "postgres:5432", "-t", "60", "--", "python", "load_historical.py"]
