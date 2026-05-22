class WebConfiguration:

    _instance = None
    config_dictionary: dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance