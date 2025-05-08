import psutil
import requests
from config import API_URL, INSTANCE_ID
from utils import setup_logger

logger = setup_logger()

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
        "ports": ports
    }

    try:
        response = requests.post(API_URL, json=payload)
        logger.info(f"Reported ports: {ports} | Status: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Failed to report ports: {e}")
