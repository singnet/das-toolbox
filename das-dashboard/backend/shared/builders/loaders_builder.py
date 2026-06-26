from shared.internal.configuration_constants import LOADERS


class LoadersBuilder:

    def build(self) -> dict:
        return {
            "metta": {"image": LOADERS["metta"]["image"]},
            "morkdb": {"image": LOADERS["morkdb"]["image"]},
        }
