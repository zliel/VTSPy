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

        # if authToken is not none, write the token to a file like "token={authToken}"
        if auth_token is not None:
            with open("token", "w") as f:
                f.write(auth_token)
                return auth_token

        # if authToken is none, return the response
        else:
            return response  # TODO: handle this error

    # make an APIStateRequest to get the current state of the API
    def get_api_state(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "APIStateRequest"
        }

        # async with connect("ws://localhost:8001") as websocket:
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
        # print(self.get_api_state(request_id=testing_id))
        print("Authentication response: ", response)
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
        print(response)


def main():
    client = VTSClient("VTSPy", "Zliel", request_id=testing_id)
    # print("Token: " + await VTSClient.get_token(client, "VTSPy", "Zliel", request_id=testing_id))
    print("Token: " + client.auth_token)
    print("Token: " + client.get_token("VTSPy", "Zliel", request_id=testing_id))
    print("API State: " + str(client.get_api_state(testing_id)))
    client.authenticate("VTSPy", "Zliel", client.auth_token, testing_id)
    client.request_stats(testing_id)


if __name__ == "__main__":
    main()
