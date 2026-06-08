FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    docker.io \
    bash-completion \
    dpkg \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /runtime_keys \
    /opt/das/.das \
    && chmod 700 /runtime_keys

ENV HOME=/opt/web-das

RUN pip install --no-cache-dir -r requirements.txt