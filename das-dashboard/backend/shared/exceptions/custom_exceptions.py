class DasCliCommandException(Exception):
    DEFAULT_MESSAGE = "There was an error while running das-cli."

    def __init__(
        self,
        message: str | None = None,
        *,
        detail: str | None = None,
        stderror: str | None = None,
    ):
        if stderror is not None:
            message = (message or "").strip() or self.DEFAULT_MESSAGE
            detail = (detail or stderror).strip()
        elif detail is None and message is not None:
            detail = str(message).strip()
            message = self.DEFAULT_MESSAGE
        else:
            message = (message or "").strip() or self.DEFAULT_MESSAGE
            detail = (detail or "").strip()

        self.message = message
        self.detail = detail
        self.stderror = detail or message
        super().__init__(self.detail or self.message)

    def __str__(self) -> str:
        if self.detail and self.detail != self.message:
            return f"{self.message}\n{self.detail}"
        return self.message

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

class DasCliResponseDecodeException(Exception):
    DEFAULT_MESSAGE = (
        "DAS-CLI returned a response in a format the server could not read. "
        "The command may have completed, but the dashboard could not confirm the result."
    )

    def __init__(self, message: str | None = None, *, detail: str | None = None):
        self.message = (message or "").strip() or self.DEFAULT_MESSAGE
        self.detail = (detail or "").strip()
        super().__init__(self.detail or self.message)

    def __str__(self) -> str:
        if self.detail and self.detail != self.message:
            return f"{self.message}\n{self.detail}"
        return self.message


# Backward-compatible alias
DASCLIResponseDecodeError = DasCliResponseDecodeException

class ConfigurationFileLoadError(Exception):

    def __init__(self, detail: str = ""):
        base_message = (
            "The DAS configuration file could not be loaded from the specified path. "
            "Please set-up services and endpoints at the configuration page."
        )
        self.detail = detail.strip()
        self.message = f"{base_message} {self.detail}".strip() if self.detail else base_message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class ConfigurationValueNotFoundError(Exception):

    def __init__(self, key: str = ""):
        base_message = (
            "Could not find specified section/value from configuration file. "
            "Please try setting up any missing services and endpoints at the configuration page."
        )
        self.key = key.strip()
        self.message = (
            f"{base_message} Missing: '{self.key}'."
            if self.key
            else base_message
        )
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

class CommandRouterConnectionError(Exception):

    def __init__(self, endpoint: str, detail: str = ""):
        self.endpoint = endpoint
        self.message = f"Could not reach the Command Router HTTP API at {endpoint}."
        self.detail = detail
        super().__init__(self.detail or self.message)

    def __str__(self) -> str:
        return self.detail or self.message