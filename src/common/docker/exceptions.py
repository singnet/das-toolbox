class DockerError(Exception):
    """Exception raised for general Docker operation errors."""

    pass


class DockerContainerDuplicateError(DockerError):
    """Exception raised when attempting to start a container that is already running."""

    pass


class DockerContextError(DockerError):
    """Exception raised for errors related to the Docker operational context."""

    pass


class DockerDaemonConnectionError(DockerError):
    """Exception raised for errors related to connecting to the Docker daemon."""

    pass


class DockerContainerNotFoundError(DockerError):
    """Exception raised when a specified container cannot be found."""

    pass


class DockerImageNotFoundError(DockerError):
    """Exception raised when a specified Docker image cannot be found."""

    pass
