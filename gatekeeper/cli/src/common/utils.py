import os
import sys
import hashlib
import platform
import uuid
import socket


def is_executable_bin() -> bool:
    return getattr(sys, "frozen", False)


def get_script_name() -> str:
    if is_executable_bin():
        return os.path.basename(sys.executable)
    else:
        return "python3 " + sys.argv[0]


def get_machine_info() -> dict:
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "node": platform.node(),
    }


def get_hardware_fingerprint() -> str:
    raw = (
        platform.node()
        + platform.machine()
        + platform.processor()
        + str(uuid.getnode())
        + socket.gethostname()
    )
    return hashlib.sha256(raw.encode()).hexdigest()
