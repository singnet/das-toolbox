class DasCliCommandException(Exception):

    def __init__(self, stderror: str):
        self.message = "There was an error while running das-cli."
        self.stderror = stderror
        super().__init__(stderror)

    def __str__(self) -> str:
        return self.stderror

class DasCliNotInstalledException(Exception):

    def __init__(self, error_message : str):

        self.message = error_message

        super().__init__(error_message)

class ConfigSaveException(Exception):
    
    def __init__(self, error_message : str, exception_message : str):
        self.message = error_message
        self.exception_message = exception_message

        super().__init(error_message)

class ProfileSaveException(Exception):

    def __init__(self, error_message : str, exception_message : str):
        self.message = error_message
        self.exception_message = exception_message

        super().__init__(error_message)

class ProfileNotFoundException(Exception):

    def __init__(self, error_message : str):

        self.message = error_message
        super().__init__(error_message)

class FileSaveException(Exception):

    def __init__(self, error_message : str):

        self.message = error_message
        super().__init__(error_message)

class FileAlreadyExistsException(Exception):

    def __init__(self, message: str, file_path: str):
        self.message = message
        self.file_path = file_path


class RemoteSshConnectionError(Exception):

    def __init__(self, message: str, *, detail: str = ""):
        self.message = message
        self.detail = detail
        super().__init__(message)


class RemoteSshTransferError(Exception):

    def __init__(self, message: str, *, detail: str = ""):
        self.message = message
        self.detail = detail
        super().__init__(message)

class CustomValueError(Exception):

    def __init__(self, message):
        self.message = message

# These exceptions will have default messages because we can't set them on service.

class WebSocketError(Exception):

    def __init__(self):
        self.message = "There was a sudden error in the socket and it had to be closed."

class WebSocketMessageDecodeError(Exception):
    
    def __init__(self):
        self.message = "The websocket encountered an error while trying to parse das-cli's response. "

class WebSocketStreamEmpty(Exception):

    def __init__(self):

        self.message = "The server's socket received an empty and unexpected response. Possibly an internal error in das-cli. Try running das-cli commands manually and check for any errors."

class DASServiceInstantiationError(Exception):

    def __init__(self):
        self.message = "There was an error while trying to resolve this service. Command cannot be executed."

class DASCLIResponseDecodeError(Exception):

    def __init__(self, detail: str = ""):
        self.message = (
            "DAS-CLI returned a message in a format the server could not read. "
            "Try running the command manually to check the results."
        )
        self.detail = detail
        super().__init__(self.detail or self.message)

    def __str__(self) -> str:
        return self.detail or self.message


class CommandRouterConnectionError(Exception):

    def __init__(self, endpoint: str, detail: str = ""):
        self.endpoint = endpoint
        self.message = f"Could not reach the Command Router HTTP API at {endpoint}."
        self.detail = detail
        super().__init__(self.detail or self.message)

    def __str__(self) -> str:
        return self.detail or self.message