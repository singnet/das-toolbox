import psutil
import requests
from config import API_URL
from utils import setup_logger
import hashlib
import platform
import uuid
import socket

logger = setup_logger()


def get_hardware_fingerprint() -> str:
    raw = (
        platform.node()
        + platform.machine()
        + platform.processor()
        + str(uuid.getnode())
        + socket.gethostname()
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def get_used_ports():
    return list({
        conn.laddr.port
        for conn in psutil.net_connections(kind='inet')
        if conn.status == psutil.CONN_LISTEN
    })

def report_ports():
    ports = get_used_ports()
    payload = {
        "instance_id": get_hardware_fingerprint(),
        "ports": ports
    }

    try:
        response = requests.post(f'{API_URL}/api/ports/observe', json=payload)
        logger.info(f"Reported ports: {ports} | Status: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Failed to report ports: {e}")
