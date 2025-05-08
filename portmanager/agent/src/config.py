import os

API_URL = os.getenv("API_URL", "http://localhost:5000/ports/observe")
INSTANCE_ID = int(os.getenv("INSTANCE_ID", 1))
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 30))
