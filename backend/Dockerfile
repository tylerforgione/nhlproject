FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y git fish curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://chatgpt.com/codex/install.sh | sh

RUN mkdir -p /root/.config/fish && \
    echo 'fish_add_path /root/.local/bin' >> /root/.config/fish/config.fish

WORKDIR /workspace/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .