from shared.builders.agents_builder import AgentsBuilder
from shared.builders.atom_db_builder import AtomDbBuilder
from shared.builders.environment_builder import EnvironmentBuilder
from shared.builders.loaders_builder import LoadersBuilder
from shared.builders.vault_builder import VaultBuilder


class ConfigMapper:

    @staticmethod
    def build_config(flat: dict, profile_username: str = "") -> dict:
        return {
            "atomdb": AtomDbBuilder(profile_username=profile_username).build(flat["atomdb"]),
            "loaders": LoadersBuilder().build(),
            "vault": VaultBuilder().build(flat.get("vault")),
            "agents": AgentsBuilder().build(flat),
            "environment": EnvironmentBuilder().build(flat["environment"]),
        }
