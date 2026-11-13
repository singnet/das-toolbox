from shared.builders.agents_builder import AgentsBuilder
from shared.builders.atom_db_builder import AtomDbBuilder
from shared.builders.db_start_targets import build_db_start_targets
from shared.builders.environment_builder import EnvironmentBuilder
from shared.builders.loaders_builder import LoadersBuilder


class ConfigMapper:

    @staticmethod
    def build_config(flat: dict, profile_username: str = "") -> dict:
        atomdb = AtomDbBuilder(profile_username=profile_username).build(flat["atomdb"])
        config = {
            "atomdb": atomdb,
            "loaders": LoadersBuilder().build(),
            "vault": flat["vault"],
            "agents": AgentsBuilder().build(flat),
            "environment": EnvironmentBuilder().build(flat["environment"]),
        }
        targets = build_db_start_targets(atomdb, profile_username)
        if targets:
            config["db_start_targets"] = targets
        return config

