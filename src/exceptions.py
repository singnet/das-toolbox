class ContainerAlreadyRunningException(Exception):
    pass


class ContainerNotRunningException(Exception):
    pass


class NotFound(Exception):
    pass


class ValidateFailed(Exception):
    pass


class DockerException(Exception):
    pass


class DockerDaemonException(Exception):
    pass
