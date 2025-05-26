import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ports.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
    JWT_ALGORITHM = "HS256"
    PORT_RANGE_START = int(os.getenv("PORT_RANGE_START", 8000))
    PORT_RANGE_END = int(os.getenv("PORT_RANGE_END", 10000))
