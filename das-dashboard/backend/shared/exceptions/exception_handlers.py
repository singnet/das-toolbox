from fastapi import FastAPI
from fastapi.responses import JSONResponse
from custom_exceptions import DasCliNotInstalledException, DasCliCommandException

class AppExceptionHandlers():

    def __init__(self, app : FastAPI):
        app.add_exception_handler(500, self.handleDasCliCommandError)

    def handleDasCliCommandError(exception : DasCliCommandException):
        return JSONResponse(
            status_code=500,
            content={"message": "There was an error running this das cli command.", "exceptionMessage": exception.message}
        )
    
    def handleDasCliNotInstalledError(exception : DasCliNotInstalledException):
        return JSONResponse(
            status_code=500,
            content={"message": "It seems DAS-CLI is not installed in this machine, make sure it is installed while running the server", "exceptionMessage": exception.message}
        )

