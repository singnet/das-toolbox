import os

API_URL = os.getenv("GATEKEEPER_API_URL", "http://localhost:5000")
INTERVAL_SECONDS = int(os.getenv("GATEKEEPER_INTERVAL_SECONDS", 30))
