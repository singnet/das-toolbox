from common.command import Command
from common.settings import Settings
from common.utils import extract_service_port

from .setup_utils import get_default_value


def jupyter_notebook_section(settings: Settings):
    jupyter_notebook_port = Command.prompt(
        "Enter the Jupyter Notebook port",
        default=extract_service_port(
            str(get_default_value(settings, "environment.jupyter.endpoint"))
        ),
    )

    return {"environment": {"jupyter": {"endpoint": f"localhost:{jupyter_notebook_port}"}}}
