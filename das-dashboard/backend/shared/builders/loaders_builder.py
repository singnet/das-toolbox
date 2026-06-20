from shared.internal.configuration_constants import CONSTANTS


class LoadersBuilder:

    def build(self) -> dict:
        return {
            "metta": {
                "image": CONSTANTS["loaders.metta.image"],
            },
            "morkdb": {
                "image": CONSTANTS["loaders.morkdb.image"],
            },
        }
