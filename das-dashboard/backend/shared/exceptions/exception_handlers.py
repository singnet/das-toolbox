from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .custom_exceptions import (
    DasCliCommandException,
    DasCliNotInstalledException,
    FileSaveException,
    FileAlreadyExistsException
)


class AppExceptionHandlers:

    def __init__(self, app: FastAPI):

        app.add_exception_handler(
            DasCliCommandException,
            self.handle_das_cli_command_error
        )

        app.add_exception_handler(
            DasCliNotInstalledException,
            self.handle_das_cli_not_installed_error
        )

        app.add_exception_handler(
            FileSaveException,
            self.handle_file_save_exception
        )

        app.add_exception_handler(
            FileAlreadyExistsException,
            self.handle_file_already_exists_error
        )

    async def handle_das_cli_command_error(
        self,
        request: Request,
        exc: DasCliCommandException
    ):
        return JSONResponse(
            status_code=500,
            content={
                "message": "There was an error running this DAS CLI command.",
                "exceptionMessage": getattr(exc, "message", str(exc))
            }
        )

    async def handle_das_cli_not_installed_error(
        self,
        request: Request,
        exc: DasCliNotInstalledException
    ):
        return JSONResponse(
            status_code=500,
            content={
                "message": "DAS-CLI is not installed on this machine.",
                "exceptionMessage": getattr(exc, "message", str(exc))
            }
        )

    async def handle_file_save_exception(
        self,
        request: Request,
        exc: FileSaveException
    ):
        return JSONResponse(
            status_code=500,
            content={
                "message": "There was an error trying to save the requested file.",
                "exceptionMessage": getattr(exc, "message", str(exc))
            }
        )

    async def handle_file_already_exists_error(
        self,
        request: Request,
        exc: FileAlreadyExistsException
    ):
        return JSONResponse(
            status_code=409,
            content={
                "message": exc.message,
                "file_path": exc.file_path
            }
        )