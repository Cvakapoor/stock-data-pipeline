FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the local files into the container
COPY . /app

# Install the required Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy wait-for-it script and make it executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Command to run the consumer script
CMD ["/wait-for-it.sh", "kafka:9092", "-t", "60", "--", "python", "consumer.py"]
