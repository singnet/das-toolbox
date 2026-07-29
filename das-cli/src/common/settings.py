from typing import Any, Dict, Optional

from common.config.core import get_core_defaults_dict

from .config.loader import ConfigLoader
from .config.store import ConfigStore


class Settings:
    def __init__(
        self,
        store: ConfigStore,
        default_loader: Optional[ConfigLoader] = None,
        raise_on_missing_file=False,
        raise_on_version_mismatch=False,
    ):
        self._store = store
        self._default_loader = default_loader

        if raise_on_missing_file:
            self.raise_on_missing_file()

        if raise_on_version_mismatch:
            self.raise_on_version_mismatch()

    def set_content(self, content: Dict[str, Any]) -> None:
        self._store.set_content(content)

    def replace_loader(self, loader: ConfigLoader) -> None:
        self._default_loader = loader

    def enable_overwrite_mode(self):
        return self._store.enable_overwrite_mode()

    def exists(self) -> bool:
        return self._store.exists()

    def rewind(self):
        return self._store.rewind()

    def get_content(self):
        return self._store.get_content()

    def get_path(self):
        return self._store.get_path()

    def set_path(self, new_file_path):
        self._store.set_path(new_file_path)

    def save_path(self):
        self._store.save_path()

    def get_dir_path(self):
        return self._store.get_dir_path()

    def get(self, key: str, fallback: Any = None) -> Any:
        if self._default_loader:
            default = self._default_loader.load().get(key, None)

            if default:
                return self._cast_type(default, type(fallback))

        return self._store.get(key, fallback)

    def set(self, key: str, value: Any):
        self._store.set(key, value)

    def save(self):
        self._store.save()

    def _cast_type(self, value, to_type):
        try:
            if to_type is bool:
                return str(value).lower() in ("true", "1", "yes")
            return to_type(value)
        except Exception:
            return value

    def validate_configuration_file(self):
        self.raise_on_missing_file()
        self.raise_on_version_mismatch()

    def raise_on_missing_file(self):
        path = self.get_path()
        store = self._store
        load_error = getattr(store, "_load_error", None)

        if hasattr(store, "file_exists") and not store.file_exists():
            raise FileNotFoundError(
                f"Configuration file not found at '{path}'. "
                "Run 'das-cli config set --file <path>' to point to an existing file, "
                "or 'das-cli config set' to create one."
            )

        if load_error is not None:
            raise ValueError(
                f"Configuration file at '{path}' could not be loaded: {load_error}. "
                "Fix the JSON and try again."
            ) from load_error

        if not self.exists():
            raise ValueError(
                f"Configuration file at '{path}' is empty. "
                "Restore a valid DAS config JSON, then run "
                "'das-cli config set --file <path>'."
            )

    def raise_on_version_mismatch(self):
        config = self._store.get_content()

        self._validate_structure(
            config,
            self._build_expected_schema(config),
        )

    def _validate_structure(
        self,
        current: dict,
        expected: dict,
        path: str = "",
    ) -> None:
        for key, expected_value in expected.items():
            current_path = f"{path}.{key}" if path else key

            if key not in current:
                raise ValueError(
                    "Your configuration file doesn't have all the entries "
                    "this version of das-cli requires. "
                    f"Missing entry: '{current_path}'. "
                    "Run 'das-cli config set' and press ENTER on the prompts "
                    "to reuse your current values and populate new fields."
                )

            current_value = current[key]

            if isinstance(expected_value, dict):
                if not isinstance(current_value, dict):
                    raise ValueError(
                        f"Invalid configuration entry '{current_path}'. " "Expected an object."
                    )

                self._validate_structure(
                    current_value,
                    expected_value,
                    current_path,
                )

    def _build_expected_schema(self, config: dict) -> dict:
        expected = get_core_defaults_dict().copy()

        atomdb_type = config.get("atomdb", {}).get("type")

        atomdb_section = expected["atomdb"]

        if atomdb_type != "adapterdb":
            atomdb_section.pop("adapterdb", None)

        if atomdb_type != "remotedb":
            atomdb_section.pop("remote_peers", None)

        if atomdb_type != "morkdb":
            atomdb_section.pop("mongodb", None)
            atomdb_section.pop("morkdb", None)

        if atomdb_type != "redismongodb":
            atomdb_section.pop("mongodb", None)
            atomdb_section.pop("redis", None)

        adapterdb = atomdb_section.get("adapterdb")

        if adapterdb:
            backend = adapterdb.get("atomdb_backend")

            if backend:
                backend_type = (
                    config.get("atomdb", {})
                    .get("adapterdb", {})
                    .get("atomdb_backend", {})
                    .get("type")
                )

            if backend_type != "redismongodb":
                backend.pop("redis", None)
                backend.pop("mongodb", None)

            if backend_type != "morkdb":
                backend.pop("morkdb", None)

            if backend_type != "inmemorydb":
                backend.pop("inmemorydb", None)

        return expected

    def pretty(self) -> str:
        table_lines = []
        obj = self.get_content()
        column_widths = {"Service": 7, "Name": 4, "Value": 5}

        def get_flattened_items(current_obj, parent_key=""):
            items = []
            if isinstance(current_obj, dict):
                for k, v in current_obj.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    items.extend(get_flattened_items(v, new_key))
            elif isinstance(current_obj, list):
                parts = parent_key.rsplit(".", 1)
                service = parts[0] if len(parts) > 1 else ""
                name = parts[-1]
                items.append((service, name, f"[{len(current_obj)} items]"))
            else:
                parts = parent_key.rsplit(".", 1)
                service = parts[0] if len(parts) > 1 else ""
                name = parts[-1]
                items.append((service, name, str(current_obj)))
            return items

        flattened_data = get_flattened_items(obj)

        for service, name, value in flattened_data:
            column_widths["Service"] = max(column_widths["Service"], len(service))
            column_widths["Name"] = max(column_widths["Name"], len(name))
            column_widths["Value"] = max(column_widths["Value"], len(value))

        column_widths["Value"] = min(column_widths["Value"], 80)

        separator = "+-{s:-<{sw}}-+-{n:-<{nw}}-+-{v:-<{vw}}-+".format(
            s="",
            sw=column_widths["Service"],
            n="",
            nw=column_widths["Name"],
            v="",
            vw=column_widths["Value"],
        )

        header = "| {s:<{sw}} | {n:<{nw}} | {v:<{vw}} |".format(
            s="Service",
            sw=column_widths["Service"],
            n="Name",
            nw=column_widths["Name"],
            v="Value",
            vw=column_widths["Value"],
        )

        table_lines.append(separator)
        table_lines.append(header)
        table_lines.append(separator)

        for service, name, value in flattened_data:
            display_value = (value[:77] + "...") if len(value) > 80 else value

            table_lines.append(
                "| {s:<{sw}} | {n:<{nw}} | {v:<{vw}} |".format(
                    s=service,
                    sw=column_widths["Service"],
                    n=name,
                    nw=column_widths["Name"],
                    v=display_value,
                    vw=column_widths["Value"],
                )
            )

        table_lines.append(separator)
        return "\n".join(table_lines)
