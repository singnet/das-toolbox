from typing import Union

import docker

from .docker_manager import DockerManager
from .exceptions import DockerError, DockerImageNotFoundError


class ImageManager(DockerManager):
    def format_function_tag(self, function, version) -> str:
        return f"{function}-{version}"

    def pull(self, repository, image_tag) -> None:
        try:
            self.get_docker_client().images.pull(repository, image_tag)
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerImageNotFoundError(
                    f"The image {repository}:{image_tag} for the function could not be located in the Docker Hub repository. Please verify the existence of the version or ensure the correct function name is used."
                )

            raise DockerError(e.explanation)

    def get_label(self, repository, tag, label) -> Union[str, None]:
        container = None

        image = f"{repository}:{tag}"

        try:
            container = self.get_docker_client().api.inspect_image(image)

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
