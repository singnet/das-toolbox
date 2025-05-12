class InstanceNotRegisteredError(Exception):
    def __init__(self, instance_id: str, message: str):
        super().__init__(f"Instance '{instance_id}' not found on server. ")
        self.instance_id = instance_id
        self.message = message


class InvalidRequestError(Exception):
    def __init__(self, message: str, payload: dict = {}):
        super().__init__(message)
        self.message = message
        self.payload = payload

class InstanceAlreadyJoinedError(Exception):
    def __init__(self, message: str, payload: dict):
        super().__init__(message)
        self.message = message
        self.payload = payload
