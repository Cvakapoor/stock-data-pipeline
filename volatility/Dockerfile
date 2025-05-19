FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install the required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy wait-for-it script and make it executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Command to run the volatility analytics script
CMD ["/bin/sh", "-c", "/wait-for-it.sh postgres:5432 -t 60 && python compute_volatility.py"]