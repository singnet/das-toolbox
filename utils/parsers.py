def table_parser(obj: dict) -> str:
    table_lines = [
        "| {:<10} | {:<15} | {:<10} |".format("Service", "Name", "Value"),
        "|{:-<12}|{:-<17}|{:-<12}|".format("", "", ""),
    ]

    def traverse_dict(current_dict, service=""):
        for key, value in current_dict.items():
            if isinstance(value, dict):
                traverse_dict(value, f"{service}{key}.")
            else:
                name = key if service else key
                service = service.strip(".")
                table_lines.append(
                    "| {:<10} | {:<15} | {:<10} |".format(service, name, value)
                )

    traverse_dict(obj)

    return "\n".join(table_lines)