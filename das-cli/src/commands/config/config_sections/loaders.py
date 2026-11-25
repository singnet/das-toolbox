from settings.config import (
    DAS_MORK_LOADER_IMAGE_NAME,
    DAS_MORK_LOADER_IMAGE_VERSION,
)


def loaders_config_section(settings):
    return {
        "loaders": {
            "metta": {"image": "none-none"},
            "morkdb": {"image": f"{DAS_MORK_LOADER_IMAGE_NAME}-{DAS_MORK_LOADER_IMAGE_VERSION}"},
        }
    }
