from common.settings import Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH
from common.container_manager.dbms.database_adapter_container_manager import DatabaseAdapterContainerManager
import os

class DatabaseAdapterFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = "das-database-adapter"

        context_mapping_paths = self._settings.get("atomdb.adapterdb.context_mapping_paths", [])
        metta_output_dir = self._settings.get("atomdb.adapterdb.export_metta_on_mapping.output_dir", "")

        return DatabaseAdapterContainerManager(
            container_name=container_name,
            options={
                    "context_mapping_paths": context_mapping_paths,
                    "metta_output_dir": metta_output_dir
                }
        )