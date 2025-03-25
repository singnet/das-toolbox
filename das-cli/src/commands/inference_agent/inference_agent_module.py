from common import Module

from .inference_agent_cli import InferenceAgentCli, InferenceAgentContainerManager, Settings


class InferenceAgentModule(Module):
    _instance = InferenceAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                InferenceAgentContainerManager,
                self._inference_agent_container_manager_factory,
            ),
        ]

    def _inference_agent_container_manager_factory(self) -> InferenceAgentContainerManager:
        container_name = self._settings.get("inference_agent.container_name")

        return InferenceAgentContainerManager(
            container_name,
            options={},
        )
