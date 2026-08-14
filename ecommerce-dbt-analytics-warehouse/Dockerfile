FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/ecommerce_analytics

ENV DBT_PROFILES_DIR=/app/ecommerce_analytics

CMD ["dbt", "build"]