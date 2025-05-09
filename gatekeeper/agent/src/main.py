import time
from config import INTERVAL_SECONDS
from observer import report_ports
from utils import setup_logger

logger = setup_logger()

def main():
    logger.info("Starting Port Observer")
    while True:
        report_ports()
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
