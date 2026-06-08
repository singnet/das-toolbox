from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

def validate_persistent_storage():
    path = Path("/opt/web-das")

    try:
        same_device = (
            path.stat().st_dev ==
            path.parent.stat().st_dev
        )

        if same_device:
            logger.error(
                "Persistent storage is not mounted on /opt/web-das. "
                "Refusing to start application."
            )

            sys.exit(1)

    except Exception:
        logger.critical(
            "INFO: Could not validate if persistent storage was created during server startup. This will cause future errors when trying to use any servers that depend on storing files."
        )

        logger.critical("INFO: Refusing to start application")

        sys.exit(1)