import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ports.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TOKEN = os.getenv("API_TOKEN", "supersecrettoken")
