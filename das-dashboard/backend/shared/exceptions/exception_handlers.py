from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .custom_exceptions import (
    DasCliCommandException,
    DasCliNotInstalledException,
    FileSaveException,
    FileAlreadyExistsException,
    DASServiceInstantiationError,
    DASCLIResponseDecodeError,
    RemoteSshConnectionError,
    RemoteSshTransferError,
    CustomValueError,
    CommandRouterConnectionError,
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

        app.add_exception_handler(
            RemoteSshConnectionError,
            self.handle_remote_ssh_connection_error,
        )

        app.add_exception_handler(
            RemoteSshTransferError,
            self.handle_remote_ssh_transfer_error,
        )

        app.add_exception_handler(
            Exception,
            self.handle_general_exception
        )

        app.add_exception_handler(
            DASServiceInstantiationError,
            self.handle_das_cli_service_error,
        )

        app.add_exception_handler(
            CustomValueError,
            self.handle_custom_value_error,
        )

        app.add_exception_handler(
            CommandRouterConnectionError,
            self.handle_command_router_connection_error,
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
                "exceptionMessage": exc.stderror
            }
        )

    async def handle_das_cli_not_installed_error(
        self,
        request: Request,
        exc: DasCliNotInstalledException
    ):
        return JSONResponse(
            status_code=404,
            content={
                "message": exc.message
            }
        )
    
    async def handle_das_cli_service_error(
        self,
        request: Request,
        exc: DASServiceInstantiationError
    ):
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message
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

    async def handle_remote_ssh_connection_error(
        self,
        request: Request,
        exc: RemoteSshConnectionError,
    ):
        content = {"message": exc.message}
        if exc.detail:
            content["exceptionMessage"] = exc.detail

        return JSONResponse(status_code=502, content=content)

    async def handle_remote_ssh_transfer_error(
        self,
        request: Request,
        exc: RemoteSshTransferError,
    ):
        content = {"message": exc.message}
        if exc.detail:
            content["exceptionMessage"] = exc.detail

        return JSONResponse(status_code=400, content=content)
    
    async def handle_command_router_connection_error(
        self,
        request: Request,
        exc: CommandRouterConnectionError,
    ):
        content = {"message": exc.message, "endpoint": exc.endpoint}
        if exc.detail:
            content["exceptionMessage"] = exc.detail

        return JSONResponse(status_code=502, content=content)

    async def handle_general_exception(
        self,
        request: Request,
        exc: Exception
    ):
        error_message = getattr(exc, "message", None)

        if not error_message:
            if exc.args:
                error_message = str(exc.args[0])
            else:
                error_message = str(exc) or "An unexpected internal server error occurred."

        return JSONResponse(
            status_code=500,
            content={
                "message": error_message
            }
        )
    
    async def das_cli_decode_error(
        self,
        request: Request,
        exc: DASCLIResponseDecodeError
    ):
        
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message
            }
        )
    
    async def handle_custom_value_error(
        self,
        request: Request,
        exc: CustomValueError,
    ):
        
        return JSONResponse(
            status_code=400,
            content={
                "message": exc.message
            }
        )