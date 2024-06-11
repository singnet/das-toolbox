from common import Module
from .jupyter_notebook_cli import JupyterNotebookCli


class JupyterNotebookModule(Module):
    _instance = JupyterNotebookCli
    _dependecy_injection = []
