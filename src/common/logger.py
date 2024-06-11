import logging
from config.config import LOG_FILE_NAME


class LoggerError(Exception): ...


class Logger:
    __instance = None

    @staticmethod
    def get_instance():
        if Logger.__instance is None:
            return Logger()
        return Logger.__instance

    def __init__(self):
        if Logger.__instance is not None:
            raise LoggerError("Invalid re-instantiation of Logger")
        else:
            logging.basicConfig(
                filename=LOG_FILE_NAME,
                format="%(asctime)s %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            Logger.__instance = self

    def _prefix(self):
        return ""

    def debug(self, msg):
        logging.debug(self._prefix() + str(msg))

    def info(self, msg):
        logging.info(self._prefix() + str(msg))

    def warning(self, msg):
        logging.warning(self._prefix() + str(msg))

    def error(self, msg):
        logging.error(self._prefix() + str(msg))

    def exception(self, msg):
        logging.exception(self._prefix() + str(msg))


def logger():
    return Logger.get_instance()
