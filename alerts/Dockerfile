FROM python:3.10-slim

WORKDIR /app

COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["/bin/sh", "-c", "/wait-for-it.sh postgres:5432 -t 60 && python alerts.py"]
