from shared.builders.agents_builder import AgentsBuilder
from shared.builders.atom_db_builder import AtomDbBuilder
from shared.builders.environment_builder import EnvironmentBuilder
from shared.builders.loaders_builder import LoadersBuilder


class ConfigMapper:

    @staticmethod
    def build_config(flat: dict, profile_username: str = "") -> dict:
        return {
            "atomdb": AtomDbBuilder(profile_username=profile_username).build(flat["atomdb"]),
            "loaders": LoadersBuilder().build(),
            "agents": AgentsBuilder().build(flat),
            "environment": EnvironmentBuilder().build(flat["environment"]),
        }
