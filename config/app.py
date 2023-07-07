# -*- coding: utf-8 -*-
import pathlib
from typing import List
from fastapi import FastAPI
import toml
# from fastapi_helper import DefaultHTTPException
# from fastapi_helper.exceptions.validation_exceptions import init_validation_handler
from pydantic import ValidationError
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from config.logger import CustomizeLogger
# from base_api.apps.frontend.router import front_router
# from base_api.config.celery_utils import create_celery
# from base_api.config.lifetime import register_shutdown_event, register_startup_event
# from base_api.config.logger import CustomizeLogger
from config.router import router


def get_project_data() -> dict:
    pyproject_path = pathlib.Path("pyproject.toml")
    pyproject_data = toml.load(pyproject_path.open())
    poetry_data = pyproject_data["tool"]["poetry"]
    return poetry_data


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        # Middleware(SQLAlchemyMiddleware),
    ]
    return middleware


def init_logging() -> None:
    config_path = pathlib.Path(__file__).parent.with_name("logger_config.json")
    CustomizeLogger.make_logger(config_path)


def get_application() -> FastAPI:
    poetry_data = get_project_data()
    app_ = FastAPI(
        title=poetry_data["name"],
        description=poetry_data["description"],
        version=poetry_data["version"],
        docs_url="/docs",
        redoc_url="/redoc",
        middleware=make_middleware(),
        # openapi_tags=metadata_tags
    )
    # app_.celery_app = create_celery()
    # init_validation_handler(app=app_)

    # register_startup_event(app_)
    # register_shutdown_event(app_)

    # app_.mount("/static", StaticFiles(directory="base_api/static"), name="static")

    app_.include_router(router)
    # app_.include_router(front_router)

    # init_logging()

    return app_


app = get_application()

# celery = app.celery_app


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    errors = []
    for each in exc.errors():
        result = {
            "code": "validation-error",
            "type": each.get("type"),
            "field": each.get("loc")[0],
            "message": each.get("msg"),
        }
        errors.append(result)

    return JSONResponse({"detail": errors}, status_code=422)


# @app.exception_handler(DefaultHTTPException)
# async def backend_validation_handler(request: Request, exc: DefaultHTTPException) -> JSONResponse:
#     content = {
#         "code": exc.code,
#         "type": exc.type,
#         "message": exc.message,
#         "field": getattr(exc, "field", '')
#     }
#     return JSONResponse(
#         {"detail": [content]},
#         status_code=exc.status_code,
#     )
#
#
# @app.exception_handler(404)
# async def custom_404_handler(_, __):
#     return RedirectResponse("/page-not-found")
