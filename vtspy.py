from websocket import create_connection
import json

testing_id = "TestingTesting123"


class VTSClient:
    def __init__(self, plugin_name: str, plugin_developer: str, plugin_logo: str = "", request_id: str = ""):
        self.instance = create_connection("ws://localhost:8001")
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.plugin_logo = plugin_logo
        self.request_id = request_id
        self.auth_token = self.get_token(plugin_name, plugin_developer, plugin_logo, request_id)

    def get_token(self, plugin_name: str, plugin_developer: str, plugin_logo: str = "", request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": plugin_name,
                "pluginDeveloper": plugin_developer,
                "pluginLogo": plugin_logo
            }
        }

        # check if the token is already in the file
        try:
            with open("token", "r") as f:
                auth_token = f.read()
                return auth_token
        except FileNotFoundError:
            pass

        # if not, get the token from the websocket
        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        auth_token = response["data"]["authenticationToken"]

        # if authToken is not none, write the token to a file
        if auth_token is not None:
            with open("token", "w") as f:
                f.write(auth_token)
                return auth_token

        # if authToken is none, return the response
        else:
            return response

    def get_api_state(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "APIStateRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    # make an AuthenticationRequest to the websocket
    def authenticate(self, plugin_name: str, plugin_developer: str, token: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": plugin_name,
                "pluginDeveloper": plugin_developer,
                "authenticationToken": token
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_stats(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "StatisticsRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_folder_info(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "VTSFolderInfoRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_current_model(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "CurrentModelRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_available_models(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "AvailableModelsRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def load_model(self, model_id: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ModelLoadRequest",
            "data": {
                "modelID": model_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def move_model_request(self, time_in_seconds: float, values_are_relative_to_model: bool, x_pos: float = None, y_pos: float = None, rotation: float = None, size: float = None, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "MoveModelRequest",
            "data": {
                "timeInSeconds": time_in_seconds,
                "valuesAreRelativeToModel": values_are_relative_to_model,
                "positionX": x_pos,
                "positionY": y_pos,
                "rotation": rotation,
                "size": size
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response


