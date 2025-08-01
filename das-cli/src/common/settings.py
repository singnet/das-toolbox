from typing import Any, Optional

from common.utils import get_schema_hash

from .config.loader import ConfigLoader
from .config.store import ConfigStore


class Settings:
    def __init__(
        self,
        store: ConfigStore,
        default_loader: Optional[ConfigLoader] = None,
        raise_on_missing_file=False,
        raise_on_schema_mismatch=False,
    ):
        self._store = store
        self._default_loader = default_loader

        if raise_on_missing_file:
            self.raise_on_missing_file()

        if raise_on_schema_mismatch:
            self.raise_on_schema_mismatch()

    def replace_loader(self, loader: ConfigLoader) -> None:
        self._default_loader = loader

    def exists(self) -> bool:
        return self._store.exists()

    def rewind(self):
        return self._store.rewind()

    def get_content(self):
        return self._store.get_content()

    def get_path(self):
        return self._store.get_path()

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

    def raise_on_schema_mismatch(self):
        expected_hash = get_schema_hash()
        if self._store.get("schema_hash") != expected_hash:
            mismatch_message = f"Your configuration file in {self.get_path()} doesn't have all the entries this version of das-cli requires. You can call 'das-cli config set' and hit <ENTER> to every prompt in order to re-use the configuration you currently have in your config file and set the new ones to safe default values."

            raise ValueError(mismatch_message)

    def raise_on_missing_file(self):
        if not self.exists():
            raise FileNotFoundError(
                f"Configuration file not found in {self.get_path()}. You can run the command `config set` to create a configuration file."
            )

    def pretty(self) -> str:
        table_lines = []
        obj = self.get_content()

        column_widths = {"Service": 7, "Name": 4, "Value": 5}

        def calculate_column_widths(current_dict, service=""):
            nonlocal column_widths

            for key, value in current_dict.items():
                if isinstance(value, dict):
                    calculate_column_widths(value, f"{service}{key}.")
                else:
                    name = key if service else key
                    service = service.strip(".")
                    column_widths["Service"] = max(column_widths["Service"], len(service))
                    column_widths["Name"] = max(column_widths["Name"], len(name))
                    column_widths["Value"] = max(column_widths["Value"], len(str(value)))

        calculate_column_widths(obj)

        table_lines.append(
            "+-{s:-<{sw}}-+-{n:-<{nw}}-+-{v:-<{vw}}-+".format(
                s="",
                sw=column_widths["Service"],
                n="",
                nw=column_widths["Name"],
                v="",
                vw=column_widths["Value"],
            )
        )

        table_lines.append(
            "| {s:<{sw}} | {n:<{nw}} | {v:<{vw}} |".format(
                s="Service",
                sw=column_widths["Service"],
                n="Name",
                nw=column_widths["Name"],
                v="Value",
                vw=column_widths["Value"],
            )
        )

        table_lines.append(
            "+-{s:-<{sw}}-+-{n:-<{nw}}-+-{v:-<{vw}}-+".format(
                s="",
                sw=column_widths["Service"],
                n="",
                nw=column_widths["Name"],
                v="",
                vw=column_widths["Value"],
            )
        )

        def fill_table_rows(current_dict, service=""):
            for key, value in current_dict.items():
                if isinstance(value, dict):
                    fill_table_rows(value, f"{service}{key}.")
                else:
                    name = key if service else key
                    service = service.strip(".")
                    table_lines.append(
                        "| {s:<{sw}} | {n:<{nw}} | {v:<{vw}} |".format(
                            s=service,
                            sw=column_widths["Service"],
                            n=name,
                            nw=column_widths["Name"],
                            v=str(value),
                            vw=column_widths["Value"],
                        )
                    )

        fill_table_rows(obj)

        # Last line of the table
        table_lines.append(
            "+-{s:-<{sw}}-+-{n:-<{nw}}-+-{v:-<{vw}}-+".format(
                s="",
                sw=column_widths["Service"],
                n="",
                nw=column_widths["Name"],
                v="",
                vw=column_widths["Value"],
            )
        )

        return "\n".join(table_lines)
