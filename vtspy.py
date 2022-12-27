from websocket import create_connection
import json


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

    def move_model_request(self, time_in_seconds: float, values_are_relative_to_model: bool, x_pos: float = None,
                           y_pos: float = None, rotation: float = None, size: float = None, request_id: str = ""):
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

    def request_current_model_hotkeys(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "HotkeysInCurrentModelRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_model_hotkeys_by_id(self, model_id: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "HotkeysInCurrentModelRequest",
            "data": {
                "modelID": model_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    # Currently not working
    # Nothing is received but in the logs for VTube Studio it says that there was a NullReferenceException: Object reference not set to an instance of an object.
    # def request_live2d_item_hotkeys(self, item_file_name, request_id: str = ""):
    #     payload = {
    #         "apiName": "VTubeStudioPublicAPI",
    #         "apiVersion": "1.0",
    #         "requestID": request_id,
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

    def request_items_list(self,
                           include_available_spots: bool = False,
                           include_item_instances_in_scene: bool = False,
                           include_available_item_files: bool = False,
                           only_items_with_file_name: str = "",
                           only_items_with_instance_id: str = "",
                           request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
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
        print(response)
        return response

    def execute_current_model_hotkey(self, hotkey_id: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "hotkeyID": hotkey_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def execute_live2d_item_hotkey(self, item_instance_id: str, hotkey_id: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "HotkeyTriggerRequest",
            "data": {
                "itemInstanceID": item_instance_id,
                "hotkeyID": hotkey_id
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_expression_state(self, give_details: bool = False, expression_file_name: str = "",
                                 request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ExpressionStateRequest",
            "data": {
                "details": give_details,
                "expressionFile": expression_file_name
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def activate_expression(self, expression_file_name: str, active: bool = True, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ExpressionActivationRequest",
            "data": {
                "expressionFile": expression_file_name,
                "active": active
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_art_mesh_list(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ArtMeshListRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def tint_art_mesh(self,
                      color_r: int = None, color_g: int = None, color_b: int = None, color_a: int = 255,
                      mix_with_scene_lighting_color: float = 1,
                      tint_all_meshes: bool = False, art_mesh_number=None, exact_name=None, name_contains=None,
                      exact_tag=None, tag_contains=None, request_id: str = ""):
        """This method will tint the art mesh(es) specified by the parameters. Be careful with the RGBA values, as they should remain between 0 and 255, and if any aren't included, the RGB parameters default to 0 and A defaults to 255.
        If you want to tint all meshes, pass in tint_all_meshes=True. If you want to tint specific meshes, pass in the art_mesh_number, exact_name, name_contains, exact_tag, or tag_contains parameters."""

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ColorTintRequest",
            "data": {
                "colorTint": {
                    "colorR": color_r,
                    "colorG": color_g,
                    "colorB": color_b,
                    "colorA": color_a,
                    "mixWithSceneLightingColor": mix_with_scene_lighting_color
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
        return response

    def request_scene_color_overlay_info(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "SceneColorOverlayInfoRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_is_face_found(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "FaceFoundRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_input_parameters(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "InputParameterListRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_parameter_value(self, parameter_name: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ParameterValueRequest",
            "data": {
                "name": parameter_name
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def request_all_parameter_values(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "Live2DParameterListRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def add_new_parameter(self, parameter_name: str, parameter_description: str, min_value: int, max_value: int,
                          default_value: int, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
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
        return response

    def delete_parameter(self, parameter_name: str, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "ParameterDeletionRequest",
            "data": {
                "parameterName": parameter_name
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def set_parameter_value(self, mode: str = "add", consider_face_found: bool = False, parameter_values=None,
                            request_id: str = ""):
        """This method will set the parameter values of the model. The mode parameter can be either "add" or "set" otherwise it will raise a ValueError,
        and the parameter_values parameter should be a list of dictionaries, each containing the id of the parameter,
        the value to set it to, and an optional "weight" value.
        If consider_face_found is True, VTube Studio will consider the face found, allowing you to control when the
        "tracking lost" animation is played."""
        if mode not in ["add", "set"]:
            raise ValueError("The mode parameter must be either 'add' or 'set'.")

        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "InjectParameterDataRequest",
            "data": {
                "mode": mode,
                "faceFound": consider_face_found,
                "parameterValues": parameter_values
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def get_current_model_physics(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "GetCurrentModelPhysicsRequest"
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def set_current_model_physics(self, strength_overrides=None, wind_overrides=None, request_id: str = ""):
        """This method will set the physics overrides of the model.
        The strength_overrides and wind_overrides parameter should be a list of dictionaries,
        each containing the id of the physics, the strength float to set it to,
        a boolean for whether to set value as the base value for physics strength or wind.
        If setBaseValue is true, the id should be omitted."""
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "SetCurrentModelPhysicsRequest",
            "data": {
                "strengthOverrides": strength_overrides,
                "windOverrides": wind_overrides
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def get_NDI_config(self, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": "NDIConfigRequest",
            "data": {
                "setNewConfig": False
            }
        }

        self.instance.send(json.dumps(payload))
        response = json.loads(self.instance.recv())
        return response

    def set_NDI_config(self, ndi_active: bool, use_ndi_5: bool, use_custom_resolution: bool, custom_width_ndi: int,
                       custom_height_ndi: int, request_id: str = ""):
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
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
        return response
