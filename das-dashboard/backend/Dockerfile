FROM python:3.12-slim

COPY . .

RUN mkdir -p /runtime_keys \
    && chmod 700 /runtime_keys

RUN ["pip", "install", "-r", "requirements.txt"]

ENTRYPOINT [ "uvicorn", "main:dashboard_app", "--port", "8000"]
