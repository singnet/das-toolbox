from shared.builders.builder_helpers import _get, _require


class EnvironmentBuilder:

    def build(self, environment: dict) -> dict:
        _require(environment, "jupyter_endpoint", label="environment")

        return {
            "jupyter": {
                "endpoint": _get(environment, "jupyter_endpoint"),
            }
        }
