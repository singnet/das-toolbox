from shared.internal.web_configuration import WebConfiguration
from services.container_services import ContainerServices
from services.profile_services import ProfileServices
from services.metrics_services import MetricsServices
from services.config_services import ConfigServices
from services.database_services import DatabaseServices
from services.workspace_services import WorkspaceServices
from services.query_services import QueryServices
from services.dashboard_services import DashboardServices

WEB_CONFIG = WebConfiguration()

DASHBOARD_SERVICES = DashboardServices(WEB_CONFIG)
CONTAINER_SERVICES = ContainerServices(WEB_CONFIG)
DATABASE_SERVICES = DatabaseServices(WEB_CONFIG)
PROFILE_SERVICES = ProfileServices(WEB_CONFIG)
METRICS_SERVICES = MetricsServices(WEB_CONFIG)
CONFIG_SERVICES = ConfigServices(WEB_CONFIG)
QUERY_SERVICES = QueryServices(WEB_CONFIG)
WORKSPACE_SERVICES = WorkspaceServices()
