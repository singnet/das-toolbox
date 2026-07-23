import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger

from shared.exceptions.exception_handlers import AppExceptionHandlers
from shared.exceptions.custom_exceptions import ConfigurationFileLoadError
from shared.internal.constants import CONFIG_PATH
from shared.utils.das_cli_config import set_das_cli_config
from shared.utils.storage_check import validate_persistent_storage
from shared.db.init_db import init_db
from services_init import WEB_CONFIG, WORKSPACE_SERVICES

# Controllers
from controllers.database_controllers import router as database_router
from controllers.container_controllers import router as container_router
from controllers.profile_controllers import router as profile_router
from controllers.config_controllers import router as config_router
from controllers.metrics_controllers import router as metrics_router
from controllers.query_controllers import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_persistent_storage()
    WORKSPACE_SERVICES.ensure_workspace()
    init_db()
    WEB_CONFIG.load_user_profile()
    try:
        WEB_CONFIG.load_config_dictionary(required=False)
    except ConfigurationFileLoadError as error:
        logger.info("Configuration not loaded at startup: %s", error)

    if os.path.exists(CONFIG_PATH):
        try:
            set_das_cli_config(CONFIG_PATH, web_config=WEB_CONFIG)
        except Exception as error:
            logger.warning("Startup das-cli config initialization failed: %s", error)

    yield


dashboard_app = FastAPI(
    title="DAS Dashboard API",
    lifespan=lifespan,
)

# Exception handelrs and middlewares
AppExceptionHandlers(dashboard_app)

dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add any new routers here:
dashboard_app.include_router(database_router)
dashboard_app.include_router(container_router)
dashboard_app.include_router(profile_router)
dashboard_app.include_router(config_router)
dashboard_app.include_router(metrics_router)
dashboard_app.include_router(query_router)