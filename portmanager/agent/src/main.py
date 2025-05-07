import time
import requests
import psutil

API_URL = "http://localhost:5000/ports/observe"
INSTANCE_ID = 1
INTERVAL_SECONDS = 30

def get_used_ports():
    return list({
        conn.laddr.port
        for conn in psutil.net_connections(kind='inet')
        if conn.status == psutil.CONN_LISTEN
    })

def report_ports():
    ports = get_used_ports()
    payload = {
        "instance_id": INSTANCE_ID,
        "used_ports": ports
    }
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Reported ports: {ports} | Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to report ports: {e}")

if __name__ == "__main__":
    while True:
        report_ports()
        time.sleep(INTERVAL_SECONDS)
