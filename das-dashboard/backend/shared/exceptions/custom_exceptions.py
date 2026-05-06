class DasCliCommandException(Exception):

    def __init__(self, error_message : str, stderror : str):

        self.message = error_message
        self.stderror = stderror

        super().__init__(error_message)

class DasCliNotInstalledException(Exception):

    def __init__(self, error_message : str):

        self.message = error_message

        super().__init__(error_message)

class ProfileSaveException(Exception):

    def __init__(self, error_message : str):

        self.message = error_message
        super().__init__(error_message)