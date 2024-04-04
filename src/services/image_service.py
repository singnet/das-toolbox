import docker
from exceptions import DockerDaemonException
from exceptions import NotFound, DockerException
from typing import Union


class ImageService:
    _instance = None

    def __init__(self) -> None:
        try:
            self._docker_client = docker.from_env()
            ImageService._instance = self
        except docker.errors.DockerException:
            raise DockerDaemonException(
                "Your Docker service appears to be either malfunctioning or not running."
            )

    @staticmethod
    def get_instance():
        if ImageService._instance is None:
            return ImageService()
        return ImageService._instance

    def pull(self, repository, image_tag) -> None:
        try:
            self._docker_client.images.pull(repository, image_tag)
        except docker.errors.APIError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE
            if e.response.reason == "Not Found":
                raise NotFound(
                    f"The image {repository}:{image_tag} for the function could not be located in the Docker Hub repository. Please verify the existence of the version or ensure the correct function name is used."
                )

            raise DockerException(e.explanation)

    def get_label(self, repository, tag, label) -> Union[dict, None]:
        container = None

        image = f"{repository}:{tag}"

        try:
            container = self._docker_client.api.inspect_image(image)

            labels = container["Config"]["Labels"]

            return labels.get(
                label,
                None,
            )
        except docker.errors.APIError:
            raise NotFound()
