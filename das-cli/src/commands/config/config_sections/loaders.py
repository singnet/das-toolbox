from settings.config import (
    DAS_MORK_LOADER_IMAGE_NAME,
    DAS_MORK_LOADER_IMAGE_VERSION,
    METTA_PARSER_IMAGE_NAME,
    METTA_PARSER_IMAGE_VERSION,
)


def loaders_config_section(settings):
    return {
        "loaders": {
            "metta": {"image": f"{METTA_PARSER_IMAGE_NAME}-{METTA_PARSER_IMAGE_VERSION}"},
            "morkdb": {"image": f"{DAS_MORK_LOADER_IMAGE_NAME}-{DAS_MORK_LOADER_IMAGE_VERSION}"},
        }
    }
