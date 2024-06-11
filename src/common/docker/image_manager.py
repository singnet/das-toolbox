import docker
from typing import Union
from .exceptions import (
    DockerDaemonConnectionError,
    DockerImageNotFoundError,
    DockerError,
)


class ImageManager:
    def __init__(self) -> None:
        try:
            self._docker_client = docker.from_env()
        except docker.errors.DockerException:
            raise DockerDaemonConnectionError(
                "Your Docker service appears to be either malfunctioning or not running."
            )

    def format_function_tag(self, function, version) -> str:
        return f"{function}-{version}"

    def pull(self, repository, image_tag) -> None:
        try:
            self._docker_client.images.pull(repository, image_tag)
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerImageNotFoundError(
                    f"The image {repository}:{image_tag} for the function could not be located in the Docker Hub repository. Please verify the existence of the version or ensure the correct function name is used."
                )

            raise DockerError(e.explanation)

    def get_label(self, repository, tag, label) -> Union[dict, None]:
        container = None

        image = f"{repository}:{tag}"

        try:
            container = self._docker_client.api.inspect_image(image)

            labels = container["Config"]["Labels"]

            if labels is None:
                return tag

            return labels.get(
                label,
                None,
            )
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerImageNotFoundError(
                    f"The image {image} for the function could not be located in the Docker Hub repository. Please verify the existence of the version or ensure the correct function name is used."
                )

            raise DockerError(e.explanation)
