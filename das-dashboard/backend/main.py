from fastapi import FastAPI
from fastapi.responses import JSONResponse
from enums.action_types import ActionTypes
from dtos.dashboard_action_dto import DashboardActionDTO

from services.container_services import ContainerServices

BASE_ENDPOINT = "/dashboard"
CONTAINER_SERVICES = ContainerServices()

dashboard_app = FastAPI()

### Dashboard Action Endpoints (Start, Stop or Restart a container/service)

@dashboard_app.post(f"{BASE_ENDPOINT}/service")
def execute_server_action(action : ActionTypes, action_request: DashboardActionDTO):

    match action:

        case ActionTypes.START:
            CONTAINER_SERVICES.start_das_cli_container(action_request)

        case ActionTypes.STOP:
            CONTAINER_SERVICES.stop_das_cli_container(action_request)

        case ActionTypes.RESTART:
            CONTAINER_SERVICES.restart_das_cli_container(action_request)

        case _:
            return JSONResponse(
                status_code=422,
                content={"msg": "Invalid specified command, please verify documentation before usage."}
            )

### Dashboard Data Endpoints (Get static info, real-time, specific service)

def get_server_info(): # Will return static info like server name/cpu/memory/disk info, info that doesn't need to be actively refreshed or re-requested
    pass
    '''
        Will return something like
        ServerInfo {
        
            Server_username:
            Running operational system:
            CPU Info (cores):
            Memory Info (total):
            Disks (what partitions/mounted FS):
            Total disk memory:
        
        }
    '''

def get_server_static_info(): # Will return static info from the server like CPU Cores, Total Memory, Total Disk(s) size,
    pass
    '''
        Will return something like
        ServerInfo {
        
            Server_username:
            Running operational system:
            CPU Info (cores):
            Memory Info (total):
            Disks (what partitions/mounted FS):
            Total disk memory:
        
        }
        '''

def get_service_static_info(): # Will return static info like names/ports for the specified service.
    pass
    '''
        Will return something like
        ServiceInfo {
        
            Service name:
            Service container name:
            Service container desc/info:
            Service port:
        
        }
        '''

def get_service_info(): # Returns non-static info for the specified service, can specify service by container_name.
    pass
    '''
    Will return something like
    ServiceInfo {
    
        CPU Avg: XX%
        CPU Now: XX%
        Memory Avg: YY%
        Memory Now: YY%
        Service name:
        Service container name:
        Service port:
        Service container status:    
        Service Health status:
        Service Age:
    
    }
    '''

