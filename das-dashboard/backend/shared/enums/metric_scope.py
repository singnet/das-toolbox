from enum import Enum

class MetricScope(Enum):
    SERVER = "server"
    SERVICE = "service"
    ALL = "all"