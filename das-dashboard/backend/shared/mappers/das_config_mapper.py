from shared.builders.agents_builder import AgentsBuilder
from shared.builders.atom_db_builder import AtomDbBuilder
from shared.builders.environment_builder import EnvironmentBuilder
from shared.builders.loaders_builder import LoadersBuilder
from shared.dtos.configuration_entries_dto import ConfigurationEntriesDto


class ConfigMapper:

    @staticmethod
    def build_config(dto: ConfigurationEntriesDto) -> dict:
        flat = dto.model_dump(by_alias=True, exclude_none=True)
        config = {}

        if dto.atomdb:
            config["atomdb"] = AtomDbBuilder().build(dto.atomdb)

        config["loaders"] = LoadersBuilder().build()
        config["agents"] = AgentsBuilder().build(flat)

        if dto.environment:
            config["environment"] = EnvironmentBuilder().build(dto.environment)

        return config
