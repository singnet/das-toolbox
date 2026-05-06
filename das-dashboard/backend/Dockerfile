FROM python:3.12-slim

WORKDIR /application

COPY . /application/

RUN ["pip", "install", "-r", "requirements.txt"]

ENTRYPOINT [ "uvicorn", "main:dashboard_app", "--port", "8000"]
