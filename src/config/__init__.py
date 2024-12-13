from .config import *


def get_config(key):
    static_values = globals()
    return static_values.get(key)
