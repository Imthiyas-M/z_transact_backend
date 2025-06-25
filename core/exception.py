from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import os

from core.custom_exception import CustomAPIException


IS_DEV = os.getenv("ENV", "dev") == "dev"

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(CustomAPIException)
    async def handle_custom_exception(request: Request, exc: CustomAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details if IS_DEV else None
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "E_VALIDATION_FAILED",
                    "message": "Request validation failed",
                    "details": exc.errors() if IS_DEV else None
                }
            }
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "E_INTERNAL",
                    "message": "An unexpected error occurred",
                    "details": {
                        "exception": str(exc),
                        "trace": "".join(traceback.format_tb(exc.__traceback__))
                    } if IS_DEV else None
                }
            }
        )
