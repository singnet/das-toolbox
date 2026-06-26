from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.exceptions.exception_handlers import AppExceptionHandlers
from shared.utils.storage_check import validate_persistent_storage
from services_init import WEB_CONFIG, WORKSPACE_SERVICES

# Controllers
from controllers.database_controllers import router as database_router
from controllers.container_controllers import router as container_router
from controllers.profile_controllers import router as profile_router
from controllers.config_controllers import router as config_router
from controllers.metrics_controllers import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_persistent_storage()
    WORKSPACE_SERVICES.ensure_workspace()
    WEB_CONFIG.load_user_profile()
    WEB_CONFIG.load_config_dictionary()
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