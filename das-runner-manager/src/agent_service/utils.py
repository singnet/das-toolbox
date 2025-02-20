import logging
import sys
from functools import wraps


def log_agent_activity(message: str):
    logging.info(message)


def handle_connection_refused(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "Connection refused" in str(e):
                print("Connection refused: The agent might not be running.")
                print(
                    "Please start the agent using the command 'restart-agent' before retrying."
                )
                sys.exit(1)
            else:
                raise e

    return wrapper
