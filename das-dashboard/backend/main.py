from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from shared.enums.action_types import ActionTypes
from shared.dtos.dashboard_action_dto import DashboardActionDTO
from shared.dtos.dashboard_profile_dto import DashboardProfileDto

from services.container_services import ContainerServices
from services.profile_services import ProfileServices

BASE_ENDPOINT = "/dashboard"

CONTAINER_SERVICES = ContainerServices()
PROFILE_SERVICES = ProfileServices()

dashboard_app = FastAPI()

dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### TODO: When everything is ready move endpoints to dedicated files

### Dashboard Action Endpoints (Start, Stop or Restart a container/service)
@dashboard_app.post(f"{BASE_ENDPOINT}/service")
def execute_server_action(action : ActionTypes, action_request: DashboardActionDTO):

    match action:

        case ActionTypes.START:
            result = CONTAINER_SERVICES.start_das_cli_container(action_request)
            return JSONResponse(status_code=200, content={"message": "Command ran succesfully with no errors.", "cli_message": result})

        case ActionTypes.STOP:
            result = CONTAINER_SERVICES.stop_das_cli_container(action_request)
            return JSONResponse(status_code=200, content={"message": "Command ran succesfully with no errors.", "cli_message": result})

        case ActionTypes.RESTART:
            result = CONTAINER_SERVICES.restart_das_cli_container(action_request)
            return JSONResponse(status_code=200, content={"message": "Command ran succesfully with no errors.", "cli_message": result})

        case _:
            return JSONResponse(
                status_code=422,
                content={"msg": "Invalid specified command, please verify documentation before usage."}
            )



### UI Profile Endpoints (Create SSH Profile)
@dashboard_app.post("/profile")
async def create_user_profile(
    dashboard_profile: DashboardProfileDto = Depends(DashboardProfileDto.as_form)
):
    await PROFILE_SERVICES.save_dashboard_profile(dashboard_profile)

    return JSONResponse(status_code=201, content={"message":"The user's SSH profile was created sucessfully."})



### Dashboard Data Endpoints (Get static info, real-time, specific service)
@dashboard_app.get(f"{BASE_ENDPOINT}/server")
def fetch_initial_server_info(): # Will return static info from the server like CPU Cores, Total Memory, Total Disk(s) size. Will also retrieve user's profile (If he has one).
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

@dashboard_app.websocket(f"{BASE_ENDPOINT}/server/ws")
def get_server_info(): # Will return non-static info like server name/cpu/memory/disk info.
    pass
    '''
        Will return something like
        ServerInfo {
        
            CPU Info (usage % current):
            Memory Info (usage % current):
            Disk usage (current):
        
        }
    '''



@dashboard_app.get(f"{BASE_ENDPOINT}/service")
def get_service_static_info(service_name : str): # Will return static or nonstatic info like names/ports for the specified service.
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

@dashboard_app.websocket(f"{BASE_ENDPOINT}/service")
def get_service_info(service_name : str): # Returns non-static info for the specified service, can specify service by container_name.
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

