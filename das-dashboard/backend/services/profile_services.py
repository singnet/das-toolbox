from shared.dtos.dashboard_profile_dto import DashboardProfileDto
import os.path
import json

EXPANDED_HOME = os.path.expanduser("~")
DEFAULT_PROFILE_PATH = os.path.join(EXPANDED_HOME, ".das", "webapp_profile.json")

class ProfileServices():

    def save_dashboard_profile(self, request : DashboardProfileDto) -> str:

        try:
            with open(DEFAULT_PROFILE_PATH, "w+") as file:
                file.write(
                    request.model_dump_json()
                )

            return "User profile was created sucessfully."
        
        except:
            return ""

    def _load_dashboard_profile(self): # Will be used in "load server static"

        file = open(DEFAULT_PROFILE_PATH, "r")
        file_json = json.loads(file.read())

        print(file_json)
    