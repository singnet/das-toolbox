from common import Module

from .attention_broker_cli import AttentionBrokerCli, AttentionBrokerManager, Settings


class AttentionBrokerModule(Module):
    _instance = AttentionBrokerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                AttentionBrokerManager,
                self._attention_broker_container_manager_factory,
            ),
        ]

    def _attention_broker_container_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_port = str(self._settings.get("attention_broker.port"))

        container_name = self._settings.get("attention_broker.container_name")

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_port": attention_broker_port,
            },
        )
