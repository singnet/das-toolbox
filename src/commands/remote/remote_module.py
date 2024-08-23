from common import Module

from .remote_cli import RemoteCli


class RemoteModule(Module):
    _instance = RemoteCli
    _dependency_injection = []
