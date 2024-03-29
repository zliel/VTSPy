from websockets.sync.client import connect
import json
import threading
import time

from vtspy import APIError


# noinspection GrazieInspection
class VTSClient:
    """
    A client for interacting with the VTubeStudio API.

    This class provides a convenient interface for sending requests to the and
    handling responses from the API. It also provides a simple way to subscribe to events
    and handle them in a se   parate thread. For more in-depth information about the API, see the
    official documentation at https://github.com/DenchiSoft/VTubeStudio

    Example:
        client = VTSClient("MyPlugin", "MyName", "iVBORw0.........KGgoA=")
        client.authenticate("my-auth-request-id")
        client.subscribe_to_event("TestEvent", on_message=print)
        time.sleep(10)
        client.unsubscribe_from_event("TestEvent")

    Warning:
        Be aware that the token is stored in a file called "token" in the same directory as the script, and
        will be used for authentication in future sessions. If you want to change the plugin information, you will have to
        delete the file.
    """

    def __init__(self, plugin_name: str, plugin_developer: str, plugin_logo: str = ""):
        """
        Initialize a new VTSClient instance.

        :param plugin_name: The name of the plugin.
        :param plugin_developer: The name of the developer of the plugin.
        :param plugin_logo: The base64-encoded logo of the plugin. This will be displayed in VTubeStudio's plugin list.
        """
        self.instance = connect("ws://localhost:8001")
        self.plugin_name = plugin_name
        self.plugin_developer = plugin_developer
        self.plugin_logo = plugin_logo
        self.default_request_id = f"{plugin_name.replace(' ', '')}Request"
        self.auth_token = self.get_token(f"TokenRequest")
        self._subscriptions = {"TestEvent": False, "ModelLoadedEvent": False, "TrackingStatusChangedEvent": False,
                               "BackgroundChangedEvent": False, "ModelConfigChangedEvent": False,
                               "ModelMovedEvent": False, "ModelOutlineEvent": False}

    def get_token(self, request_id: str = ""):
        """
        This method will return a token for the plugin to use for authentication.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#authentication

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the authentication token.
        :raises APIError: If the token file cannot be found and the plugin isn't allowed by the user.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "pluginLogo": self.plugin_logo
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
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        auth_token = response["data"]["authenticationToken"]

        # if authToken is not none, write the token to a file
        if auth_token is not None:
            with open("token", "w") as f:
                f.write(auth_token)
                return auth_token

        # if authToken is none, return the response
        else:
            return response

    def get_api_state(self, request_id: str = "") -> dict:
        """
        This method will return the current state of the VTubeStudio session.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#api-details

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain whether the API is enabled, the VTubeStudio version, and whether the plugin is
        authenticated for the current session.
        :raises APIError: If VTubeStudio is not running.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "APIStateRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def authenticate(self, request_id: str = "") -> dict:
        """
        This method will authenticate the plugin with VTubeStudio.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#authentication

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the authentication token if it's the first time the plugin has been authenticated, or
        a boolean value indicating the plugin has been authenticated.
        :raises APIError: If the plugin is not allowed by the user.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "pluginLogo": self.plugin_logo,
                "authenticationToken": self.auth_token
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_stats(self, request_id: str = "") -> dict:
        """
        This method will return statistics about the current VTubeStudio session (things like uptime, framerate, number of plugins, resolution, etc.).
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#getting-current-vts-statistics

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain a dictionary of the statistics.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "StatisticsRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_folder_info(self, request_id: str = "") -> dict:
        """
        This method will return the names of the folders in the VTubeStudio "StreamingAssets" folder.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#getting-list-of-vts-folders

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain a dictionary of the folder types and names.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "VTSFolderInfoRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_current_model_info(self, request_id: str = "") -> dict:
        """
        This method will return information about the current model from VTubeStudio.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#getting-the-currently-loaded-model

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain information about the current model.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "CurrentModelRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_available_models(self, request_id: str = "") -> dict:
        """
        This method will return a list of all available models from VTubeStudio.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#getting-a-list-of-available-vts-models

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain a list of all available models.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "AvailableModelsRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def load_model(self, model_id: str, request_id: str = "") -> dict:
        """
        This method will load a model into VTubeStudio. This has a 2 second global cooldown.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#loading-a-vts-model-by-its-id

        :param model_id: The ID of the model to load.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the ID of the model that was loaded.
        :raises APIError: If the plugin is not authenticated or if the model ID is invalid.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ModelLoadRequest",
            "data": {
                "modelID": model_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def move_model(self, time_in_seconds: float, values_are_relative_to_model: bool, x_pos: float = None,
                   y_pos: float = None, rotation: float = None, size: float = None,
                   request_id: str = "") -> dict:
        """
        This method will move, rotate and/or resize the current model.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#moving-the-currently-loaded-vts-model

        :param time_in_seconds: The time in seconds the movement should take. Values must be between 0 and 2.
        :param values_are_relative_to_model: If true, the values will be relative to the current model. If false, the values will be considered absolute.
        :param x_pos: The x position of the model. Values must be between -1000 and 1000.
        :param y_pos: The y position of the model. Values must be between -1000 and 1000.
        :param rotation: The rotation of the model. Values must be between -360 and 360.
        :param size: The size of the model. Values must be between -100 and 100.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio. Note that this response won't contain anything in the "data" field.
        :raises APIError: If the plugin is not authenticated, if no model is loaded, if the model is unable to move (such as while in a config window), or if the values are invalid.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
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
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_current_model_hotkeys(self, request_id: str = "") -> dict:
        """
        This method will return the current model's hotkeys
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-list-of-hotkeys-available-in-current-or-other-vts-model

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the list of hotkeys.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "HotkeysInCurrentModelRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_model_hotkeys_by_id(self, model_id: str, request_id: str = "") -> dict:
        """
        This method will return the hotkeys of the model with the given modelID.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-list-of-hotkeys-available-in-current-or-other-vts-model

        :param model_id: The modelID of the model
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the list of hotkeys.
        :raises APIError: If the plugin is not authenticated, or if the model ID is invalid/no model with that ID is found.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "HotkeysInCurrentModelRequest",
            "data": {
                "modelID": model_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    # Currently not working
    # Nothing is received but in the logs for VTube Studio it says that there was a NullReferenceException: Object reference not set to an instance of an object.
    # def get_live2d_item_hotkeys(self, item_file_name, request_id: str = "):
    #     payload = {
    #         "apiName": "VTubeStudioPublicAPI",
    #         "apiVersion": "1.0",
    #         "requestID": request_id if request_id != " else self.default_request_id,
    #         "messageType": "HotkeysInCurrentModelRequest",
    #         "data": {
    #             "live2DItemFileName": item_file_name
    #         }
    #     }
    #
    #     print("requesting hotkeys for live2d item")
    #     self.instance.send(json.dumps(payload))
    #     print("sent request")
    #     response = json.loads(self.instance.recv())
    #     print(response)
    #     return response

    def get_items_list(self,
                       include_available_spots: bool = False,
                       include_item_instances_in_scene: bool = False,
                       include_available_item_files: bool = False,
                       only_items_with_file_name: str = "",
                       only_items_with_instance_id: str = "",
                       request_id: str = "") -> dict:
        """
        This method will return a list of items, depending on the parameters set.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-list-of-available-items-or-items-in-scene

        :param include_available_spots: If true, the list will include all available spots for items to be loaded into.
        :param include_item_instances_in_scene: If true, the list will include all items that are currently loaded into the scene.
        :param include_available_item_files: If true, the list will include all available item files that can be loaded into the scene.
        :param only_items_with_file_name: If set, the list will only include items that have the specified file name.
        :param only_items_with_instance_id: If set, the list will only include the item that has the specified instance ID.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the list of items.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemListRequest",
            "data": {
                "includeAvailableSpots": include_available_spots,
                "includeItemInstancesInScene": include_item_instances_in_scene,
                "includeAvailableItemFiles": include_available_item_files,
                "onlyItemsWithFileName": only_items_with_file_name,
                "onlyItemsWithInstanceID": only_items_with_instance_id
            }
        }
        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def execute_current_model_hotkey(self, hotkey_id: str, request_id: str = "") -> dict:
        """
        This method will execute the hotkey with the given ID in the currently loaded model.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-execution-of-hotkeys

        WARNING: This method will cause a permanent loop if there is no model loaded.

        :param hotkey_id: The ID of the hotkey to execute.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the ID of the hotkey that was executed.
        :raises APIError: If the plugin is not authenticated, or if the hotkey ID is invalid/no hotkey with that ID is found.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": hotkey_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def execute_live2d_item_hotkey(self, item_instance_id: str, hotkey_id: str, request_id: str = "") -> dict:
        """
        This method will execute the hotkey of a Live2D item with the given ID.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-execution-of-hotkeys

        :param item_instance_id: The ID of the Live2D item instance.
        :param hotkey_id: The ID of the hotkey to execute.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the ID of the hotkey that was executed.
        :raises APIError: If the plugin is not authenticated, if no Live2D item with the given instance ID is loaded, or if the hotkey ID is invalid/no hotkey with that ID is found.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "itemInstanceID": item_instance_id,
                "hotkeyID": hotkey_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_expression_state(self, give_details: bool = False, expression_file_name: str = "",
                             request_id: str = "") -> dict:
        """
        This method will return either the current state of a specified expression or the current state of all expressions.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-current-expression-state-list

        :param give_details: If set to true, the response will contain arrays of hotkeys and parameters the expression is used in.
        :param expression_file_name: The file name of the expression to get the state of. If this is empty, the state of all expressions will be returned.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain information about the model and the state of its expression(s).
        :raises APIError: If the plugin is not authenticated, or if the expression file name is invalid/no expression with that file name is found.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ExpressionStateRequest",
            "data": {
                "details": give_details,
                "expressionFile": expression_file_name
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def activate_expression(self, expression_file_name: str, active: bool = True, request_id: str = "") -> dict:
        """
        This method will activate or deactivate an expression. If the expression is already active or inactive, nothing will happen.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-activation-or-deactivation-of-expressions

        :param expression_file_name: The file name of the expression.
        :param active: Whether the expression should be activated or deactivated.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio. Note that this response won't contain anything in the "data" field.
        :raises APIError: If the plugin is not authenticated, or if the expression file name is invalid/no expression with that file name is found.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": expression_file_name,
                "active": active
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_art_mesh_list(self, request_id: str = "") -> dict:
        """
        This method will return a list of all art meshes in the current model.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-list-of-artmeshes-in-current-model

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain lists of the art mesh names and tags.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,

            "messageType": "ArtMeshListRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def tint_art_mesh(self,
                      color_r: int = 255, color_g: int = 255, color_b: int = 255, color_a: int = 255,
                      rainbow: bool = False,
                      mix_with_scene_lighting_color: float = None,
                      tint_all_meshes: bool = False, art_mesh_number: list[int] = None, exact_name: list[str] = None,
                      name_contains: list[str] = None, exact_tag: list[str] = None, tag_contains: list[str] = None,
                      request_id: str = "") -> dict:
        """
        This method will tint the art mesh(es) specified by the parameters. Note that if no color values are passed in, the colors will default to 255, resetting the color.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#tint-artmeshes-with-color

        :param color_r: The red value of the color to tint the art mesh(es) with. Should be between 0 and 255.
        :param color_g: The green value of the color to tint the art mesh(es) with. Should be between 0 and 255.
        :param color_b: The blue value of the color to tint the art mesh(es) with. Should be between 0 and 255.
        :param color_a: The alpha value of the color to tint the art mesh(es) with. Should be between 0 and 255.
        :param rainbow: Whether the art mesh(es) should be tinted with a rainbow color. Note that this will override the color parameters.
        :param mix_with_scene_lighting_color: The amount to mix the color with the scene lighting color. Should be between 0 and 1.
        :param tint_all_meshes: Whether or not to tint all art meshes. If this is True, the next parameters will be ignored.
        :param art_mesh_number: A list of integers that selects meshes based on their order in the model.
        :param exact_name: A list of names to search for. The name must match exactly.
        :param name_contains: The name of the art mesh(es) to tint, if the name contains this string.
        :param exact_tag: A list of tags to search for. If the art mesh(es) have all of these tags, they will be tinted.
        :param tag_contains: A list of tags to tint the art mesh(es) with, if the tag contains the contained string.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the number of art meshes matched/tinted.
        :raises APIError: If the plugin is not authenticated, if no model is currently loaded, or if the parameters are invalid.
        """

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ColorTintRequest",
            "data": {
                "colorTint": {
                    "colorR": color_r,
                    "colorG": color_g,
                    "colorB": color_b,
                    "colorA": color_a,
                    "mixWithSceneLightingColor": mix_with_scene_lighting_color,
                    "jeb_": rainbow
                },
                "artMeshMatcher": {
                    "tintAll": tint_all_meshes,
                    "artMeshNumber": art_mesh_number,
                    "nameExact": exact_name,
                    "nameContains": name_contains,
                    "tagExact": exact_tag,
                    "tagContains": tag_contains
                }
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_scene_color_overlay_info(self, request_id: str = "") -> dict:
        """
        This method will return information about the scene lighting overlay color, which overlays the user's model with
        the average color captured from a screen or window. More information can be found here: https://github.com/DenchiSoft/VTubeStudio#getting-scene-lighting-overlay-color

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain information regarding the scene lighting overlay color. Check the documentation for more specifics.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "SceneColorOverlayInfoRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def is_face_found(self, request_id: str = "") -> dict:
        """
        This method will return a boolean value indicating whether or not the face is currently being tracked.
        More information on the face tracking system can be found here: https://github.com/DenchiSoft/VTubeStudio#checking-if-face-is-currently-found-by-tracker

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain a "found" boolean value.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "FaceFoundRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_input_parameters(self, request_id: str = "") -> dict:
        """
        This method will return lists of all input parameters that are currently available in VTubeStudio, both custom and default.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#requesting-list-of-available-tracking-parameters

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain a list of custom parameters and a list of default parameters.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "InputParameterListRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_parameter_value(self, parameter_name: str, request_id: str = "") -> dict:
        """
        This method retrieves the value of a specific default or custom parameter.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#get-the-value-for-one-specific-parameter-default-or-custom.

        :param parameter_name: The name of the parameter to retrieve the value of.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain information about the parameter.
        :raises APIError: If the plugin is not authenticated or if the requested parameter does not exist.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ParameterValueRequest",
            "data": {
                "name": parameter_name
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_all_parameter_values(self, request_id: str = "") -> dict:
        """
        This method retrieves all Live2D parameter values for the current model.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#get-the-value-for-all-live2d-parameters-in-the-current-model

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain a list of all parameter values.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "Live2DParameterListRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def add_new_parameter(self, parameter_name: str, parameter_description: str, min_value: int, max_value: int,
                          default_value: int, request_id: str = "") -> dict:
        """
        This method will add a custom parameter to the model. More information can be found here: https://github.com/DenchiSoft/VTubeStudio#adding-new-tracking-parameters-custom-parameters.

        :param parameter_name: The name of the parameter. Names must be unique, alphanumeric and between 4 and 32 characters long.
        :param parameter_description: A description of what the does and how the user should use it. It should be less than 256 characters long.
        :param min_value: The minimum value the parameter can be set to. Valid values are between -1000000 and 1000000.
        :param max_value: The maximum value the parameter can be set to. Valid values are between -1000000 and 1000000.
        :param default_value: The default value the parameter will be set to when the model is loaded. Valid values are between -1000000 and 1000000.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the name of the parameter that was created.
        :raises APIError: If the plugin is not authenticated, if any of input values are invalid, if the parameter name is already in use or if there are too many parameters already (300 global and 100 per plugin maximum).
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ParameterCreationRequest",
            "data": {
                "parameterName": parameter_name,
                "explanation": parameter_description,
                "min": min_value,
                "max": max_value,
                "defaultValue": default_value
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def delete_parameter(self, parameter_name: str, request_id: str = "") -> dict:
        """
        This method will delete a custom parameter from the model. Note that default parameters cannot be deleted.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#delete-custom-parameters

        :param parameter_name: The name of the parameter to delete.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio, whose "data" object will contain the name of the parameter that was deleted.
        :raises APIError: If the plugin is not authenticated, if the parameter does not exist, or if the parameter was not added by the plugin.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ParameterDeletionRequest",
            "data": {
                "parameterName": parameter_name
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def set_parameter_value(self, mode: str = "add", consider_face_found: bool = False, parameter_values=None,
                            request_id: str = "") -> dict:
        """
        This method will set the parameter values of the model. More information can be found here: https://github.com/DenchiSoft/VTubeStudio#feeding-in-data-for-default-or-custom-parameters.

        :param mode: The mode to set the parameters in. Can be either "add" or "set". "set" will only allow one plugin to change a parameter value at a time, while "add" will allow multiple plugins to change the same parameter value at the same time.
        :param consider_face_found: Whether or not to consider the face found. If True, VTube Studio will consider the face found, allowing you to control when the "tracking lost" animation is played.
        :param parameter_values: A list of dictionaries, each containing the id of the parameter, the value to set it to, and an optional "weight" value.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio. Note that this response won't contain anything in the "data" field.
        :raises APIError: If the plugin is not authenticated, if the mode or parameter values are invalid, or if the parameter does not exist.
        """
        if mode not in ["add", "set"]:
            raise ValueError("The mode parameter must be either 'add' or 'set'.")

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "InjectParameterDataRequest",
            "data": {
                "mode": mode,
                "faceFound": consider_face_found,
                "parameterValues": parameter_values
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_current_model_physics(self, request_id: str = "") -> dict:
        """
        This method will return the current physics settings of the model More information can be found here: https://github.com/DenchiSoft/VTubeStudio#getting-physics-settings-of-currently-loaded-vts-model.

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain the user's NDI configuration properties.
        :raises APIError: If the plugin is not authenticated.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "GetCurrentModelPhysicsRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def set_current_model_physics(self, strength_overrides=None, wind_overrides=None, request_id: str = "") -> dict:
        """
        This method will set the override the physics configuration of the model.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#overriding-physics-settings-of-currently-loaded-vts-model

        :param strength_overrides: A list of dictionaries containing the id of the physics, the strength float to set it to, the length of time to override the physics for, and a boolean for whether to set value as the base value for physics strength.
        :param wind_overrides: A list of dictionaries containing the id of the physics, the wind float to set it to, the length of time to override the physics for,, and a boolean for whether to set value as the base value for wind physics.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio. Note that this response won't contain anything in the "data" field.
        :raises APIError: If the plugin is not authenticated, if the strength or wind overrides are invalid, if another plugin is already overriding the physics, or if no model is loaded.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "SetCurrentModelPhysicsRequest",
            "data": {
                "strengthOverrides": strength_overrides,
                "windOverrides": wind_overrides
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_NDI_config(self, request_id: str = "") -> dict:
        """
        This method will return the current NDI configuration. More information can be found here: https://github.com/DenchiSoft/VTubeStudio#get-and-set-ndi-settings

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain the user's NDI configuration properties.
        :raises APIError: If the plugin is not authenticated, or if this method is called within 3 seconds of a different call to the "NDIConfigRequest" endpoint.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "NDIConfigRequest",
            "data": {
                "setNewConfig": False
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def set_NDI_config(self, ndi_active: bool, use_ndi_5: bool, use_custom_resolution: bool, custom_width_ndi: int = -1,
                       custom_height_ndi: int = -1, request_id: str = "") -> dict:
        """
        This method will set the NDI configuration.
        More information can be found here: https://github.com/DenchiSoft/VTubeStudio#get-and-set-ndi-settings

        :param ndi_active: Whether to enable NDI.
        :param use_ndi_5: Whether to use NDI 5.0. If ndi_active is True, this will enable NDI 5.0.
        :param use_custom_resolution: Whether to use a custom resolution. If ndi_active is True, the height and width of the NDI stream will be set to the values of custom_width_ndi and custom_height_ndi.
        :param custom_width_ndi: The width of the NDI stream. If ndi_active is True and use_custom_resolution is True, the width of the NDI stream will be set to this value. If left empty, this will be ignored.
        :param custom_height_ndi: The height of the NDI stream. If ndi_active is True and use_custom_resolution is True, the height of the NDI stream will be set to this value. If left empty, this will be ignored.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain a list of the instance IDs and filenames of the unloaded items.
        :raises APIError: If the plugin is not authenticated, or if this method is called within 3 seconds of a different call to the "NDIConfigRequest" endpoint.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "NDIConfigRequest",
            "data": {
                "setNewConfig": True,
                "ndiActive": ndi_active,
                "useNDI5": use_ndi_5,
                "useCustomResolution": use_custom_resolution,
                "customWidthNDI": custom_width_ndi,
                "customHeightNDI": custom_height_ndi
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def load_item(self, file_name: str,
                  x_pos: float = None, y_pos: float = None, size: float = None, rotation: float = None,
                  fade_time: float = 0, order: int = 0, fail_if_order_taken: bool = False,
                  smoothing: float = 0, censored: bool = False, flipped: bool = False, locked: bool = False,
                  unload_when_plugin_disconnects: bool = True, request_id: str = "") -> dict:
        """
        This method will load an item into the scene.
        More information about the request can be found here: https://github.com/DenchiSoft/VTubeStudio#loading-item-into-the-scene

        :param file_name: The file name of the item to load. This can be found using the request_item_list() method.
        :param x_pos: The x position to load the item to. Valid values are between -1000 and 1000; check the documentation for more information about the coordinate system.
        :param y_pos: The y position to load the item to. Valid values are between -1000 and 1000; check the documentation for more information about the coordinate system.
        :param size: The initial size of the item. Valid values are between 0 and 1, with 0.32 being roughly the default size.
        :param rotation: The initial rotation of the item. Valid values are between -360 and 360.
        :param fade_time: The time it takes for the item to fade in. Valid values are between 0 and 2.
        :param order: The sorting order of the item in the scene.
        :param fail_if_order_taken: If True, the item will not be loaded if the order is already taken.
        :param smoothing: The smoothing of the item. Valid values are between 0 and 1.
        :param censored: Whether to censor the item.
        :param flipped: Whether to flip the item.
        :param locked: Whether to lock the item.
        :param unload_when_plugin_disconnects: Garbage collection. If True, the item will be unloaded when the plugin disconnects.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain the instance ID of the item.
        :raises APIError: If the plugin is not authenticated, if the input values are invalid, if no item with the
                given file name exists, if the scene is full, or if the user can't load items, such as while in a config menu.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemLoadRequest",
            "data": {
                "fileName": file_name,
                "positionX": x_pos,
                "positionY": y_pos,
                "size": size,
                "rotation": rotation,
                "fadeTime": fade_time,
                "order": order,
                "failIfOrderTaken": fail_if_order_taken,
                "smoothing": smoothing,
                "censored": censored,
                "flipped": flipped,
                "locked": locked,
                "unloadWhenPluginDisconnects": unload_when_plugin_disconnects
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def unload_all_items(self, request_id: str = "") -> dict:
        """
        This method will unload all items from the scene, regardless of what plugin loaded them.

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain a list of the instance IDs and filenames of the unloaded items.
        :raises APIError: If the plugin is not authenticated or if the user can't unload items, such as while in a config menu.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemUnloadRequest",
            "data": {
                "unloadAllInScene": True
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def unload_all_plugin_items(self, request_id: str = "") -> dict:
        """
        This method will unload all items from the scene that were loaded by your plugin. Note that this will not unload items loaded by other plugins.

        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain a list of the instance IDs and filenames of the unloaded items.
        :raises APIError: If the plugin is not authenticated or if the user can't unload items, such as while in a config menu.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemUnloadRequest",
            "data": {
                "unloadAllInScene": False,
                "unloadAllLoadedByThisPlugin": True
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def unload_items(self, allow_unloading_other_plugin_items: bool = True,
                     item_ids: list[str] = None, file_names: list[str] = None, request_id: str = "") -> dict:
        """
        This method will unload specific items from the scene.

        :param allow_unloading_other_plugin_items: If this is set to true, the plugin will be allowed to unload items that were loaded by other plugins.
        :param item_ids: A list of item IDs to unload.
        :param file_names: A list of file names to unload.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio whose "data" object will contain a list of the instance IDs and filenames of the unloaded items.
        :raises APIError: If the plugin is not authenticated or if the user can't unload items, such as while in a config menu.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemUnloadRequest",
            "data": {
                "unloadAllInScene": False,
                "unloadAllLoadedByThisPlugin": False,
                "allowUnloadingItemsLoadedByUserOrOtherPlugins": allow_unloading_other_plugin_items,
                "instanceIDs": item_ids,
                "fileNames": file_names
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def control_item_animation(self, item_instance_id: str, framerate: int = -1, frame: int = -1,
                               brightness: float = -1, opacity: float = -1,
                               set_auto_stop_frames: bool = False, auto_stop_frames=None,
                               set_animation_play_state: bool = True, animation_play_state: bool = True,
                               request_id: str = "") -> dict:
        """
        This method will control the animation of an item.

        :param item_instance_id: The instance ID of the item to control, which can be found in the response of the request_items_list() method.
        :param framerate: The framerate to set the item to. Valid values are only between 0.1 and 120.
        :param frame: The frame to set the item to. Valid values are only between 0 and the number of frames in the animation, which can be found in the response of the request_items_list() method.
        :param brightness: The brightness to set the item to. Valid values are between 0 and 1.
        :param opacity: The opacity to set the item to. Valid values are between 0 and 1.
        :param set_auto_stop_frames: Whether to allow setting specific frames for the animation to stop playing on. If this is False, the auto_stop_frames parameter will be ignored.
        :param auto_stop_frames: A list of frames for the animation to stop playing on, with a maximum size of 1024. For this to take effect, set_auto_stop_frames must be set to True.
                Valid values are only between 0 and the number of frames in the animation, which can be found in the response of the request_items_list() method.
        :param set_animation_play_state: Whether to allow setting the animation to play or pause. If this is False, the animation_play_state parameter will be ignored.
        :param animation_play_state: Whether to play (True) or pause (False) the animation. For this to take effect, set_animation_play_state must be set to True.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio.
        :raises APIError: If the plugin is not authenticated, if no item with the given instance ID exists,
                if the requested item is a Live2D item, if the input values are invalid, or if the animation is trying to be performed on a "simple" item (PNG/JPG etc.).
                Note that things like transparency and brightness are supported for "simple" items, but not animation.
        """

        if auto_stop_frames is None:
            auto_stop_frames = []

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemAnimationControlRequest",
            "data": {
                "itemInstanceID": item_instance_id,
                "framerate": framerate,
                "frame": frame,
                "brightness": brightness,
                "opacity": opacity,
                "setAutoStopFrames": set_auto_stop_frames,
                "autoStopFrames": auto_stop_frames,
                "setAnimationPlayState": set_animation_play_state,
                "animationPlayState": animation_play_state
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def move_item(self, items_to_move: list[dict] = None, request_id: str = "") -> dict:
        """This method will move items in the scene. You can move multiple items at once by passing a list of items to move.
        Information about what each dictionary in the list should contain can be found here: https://github.com/DenchiSoft/VTubeStudio#moving-items-in-the-scene

        :param items_to_move: A list of dictionaries containing information about the items to move.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio.
        :raises APIError: If the plugin is not authenticated, if the motion values are invalid, if there is no item loaded with one of the item instance IDs provided,
        if the item order was taken or if an item can't change order, such as while in a config menu.
        """

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ItemMoveRequest",
            "data": {
                "itemsToMove": items_to_move
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def get_art_mesh_selection(self, description: str = "", help_text: str = "",
                               number_of_meshes_to_select: int = 1, active_meshes: list[str] = None,
                               request_id: str = "") -> dict:
        """
        This method will present a dialogue box to the user to select meshes.
        More information about this request can be found here: https://github.com/DenchiSoft/VTubeStudio#asking-user-to-select-artmeshes

        :param description: A description that is shown to the user in the dialogue box. If left empty, VTubeStudio will use a default description.
        :param help_text: Text that will be displayed to the user when they click the "?" button. If left empty, VTubeStudio will use default text.
        :param number_of_meshes_to_select: The number of meshes that the user should select. The user will not be able to proceed until they have selected the at least this many meshes.
        :param active_meshes: A list of mesh names that should already be active when the dialogue box opens for the user.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio.
        :raises APIError: If the plugin is not authenticated.
        """

        if active_meshes is None:
            active_meshes = []

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "ArtMeshSelectionRequest",
            "data": {
                "textOverride": description,
                "helpOverride": help_text,
                "requestedArtMeshCount": number_of_meshes_to_select,
                "activeArtMeshes": active_meshes
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])
        return response

    def subscribe_to_event(self, event_name: str, on_message: callable, config: dict = None,
                           request_id: str = "") -> dict:
        """
        This method will subscribe to a specific event, calling the function passed in to the on_message parameter on the received message. It opens a new thread to listen for event messages,
        and will only close after using the unsubscribe_from_event() method. Different events will require different configuration options and have different data in the message,
        so you will need to check the documentation for each event, located here: https://github.com/DenchiSoft/VTubeStudio/tree/master/Events

        :param event_name: The name of the event to subscribe to.
        :param on_message: The function to call when a message is received from the Event API.
            The function must accept a single parameter, which will be the message received.
        :param config: A dictionary of configuration options to pass to the event.
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio.
        :raises APIError: If the plugin is not authenticated, if there is no event with the name provided, or if the configuration options are invalid.
        """
        if config is None:
            config = {}

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "EventSubscriptionRequest",
            "data": {
                "eventName": event_name,
                "subscribe": True,
                "config": config
            }
        }

        self.instance.send(json.dumps(payload))

        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])

        # Using the self._subscriptions dictionary to store the events the plugin is subscribed to
        self._subscriptions[event_name] = True

        # Upon subscribing to an event, the self._subscriptions dictionary will be updated and a thread will be started to listen for messages
        def listener():
            while self._subscriptions[event_name] is True:
                message = self.instance.recv()
                on_message(json.loads(message))

                # With the larger sleep time of 1 second, the "ModelOutlineEvent" would send too many messages, and the connection would be closed, so I changed it to 0.05 seconds
                if event_name != "ModelOutlineEvent":
                    time.sleep(1)
                else:
                    time.sleep(0.05)

        thread = threading.Thread(target=listener)
        thread.start()
        return response

    def unsubscribe_from_event(self, event_name: str, request_id: str = "") -> dict:
        """
        This method will unsubscribe from a specific event and close the thread listening for its messages.

        :param event_name: The name of the event to unsubscribe from
        :param request_id: A unique ID to identify the request. If left blank, a default ID will be used (f"{plugin_name.replace(' ', '')}Request").

        :return: The response from VTubeStudio
        :raises APIError: If the plugin is not authenticated or if there is no event with the name provided.
        """
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id if request_id != "" else self.default_request_id,
            "messageType": "EventSubscriptionRequest",
            "data": {
                "eventName": event_name,
                "subscribe": False
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        if response["messageType"] == "APIError":
            raise APIError(response["data"]["message"], response["data"]["errorID"])

        # Using the self._subscriptions dictionary to store the events the plugin is subscribed to
        self._subscriptions[event_name] = False
        return response

if __name__ == '__main__':
    client = VTSClient("VTubeStudioPublicAPI", "1.0")