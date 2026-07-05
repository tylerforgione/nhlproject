FROM python:3.12-slim

RUN apt-get update && apt-get install -y git fish && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .