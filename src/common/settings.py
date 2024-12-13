import os

from common.json_handler import JsonHandler
from config.config import get_config


class Settings(JsonHandler):
    _default_config_path = os.path.expanduser(get_config("SECRETS_PATH"))

    def __init__(self, raise_on_missing_file=False):
        super().__init__(self._default_config_path)

        if raise_on_missing_file:
            self.raise_on_missing_file()

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
