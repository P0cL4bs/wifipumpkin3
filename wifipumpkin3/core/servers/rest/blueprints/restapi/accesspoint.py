from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3 import PumpkinShell
from wifipumpkin3.core.common.platforms import Linux as Refactor
from netaddr import EUI
from flask_restful import Resource
from flask import jsonify, request
from wifipumpkin3.core.servers.rest.ext.auth import token_required
from wifipumpkin3.core.servers.rest.ext.exceptions import exception

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class ClientsResource(Resource):
    def __init__(self):
        self.root = PumpkinShell.getInstance()
        super(ClientsResource, self).__init__()

    def get_mac_vendor(self, mac):
        """ discovery mac vendor by mac address """
        try:
            d_vendor = EUI(mac)
            d_vendor = d_vendor.oui.registration().org
        except:
            d_vendor = "unknown vendor"
        return d_vendor

    @token_required
    def get(self):
        proxy_plugins = self.root.proxy_controller.getInfo()
        connected_clints = Refactor.readFileDataToJson(C.CLIENTS_CONNECTED)
        list_clients_connted = []
        for item in connected_clints:
            connected_clints[item]["VENDOR"] = self.get_mac_vendor(
                connected_clints[item]["MAC"]
            )
            list_clients_connted.append(connected_clints[item])
        return jsonify({"clients": list_clients_connted})


class SettingsAPmodeResource(Resource):
    config = SettingsINI.getInstance()
    key_name = "ap_mode"

    @token_required
    def get(self, attribute=None):
        if attribute:
            if not attribute in self.config.get_all_childname(self.key_name):
                return exception(
                    "Cannot found that attribute {} on {}!".format(
                        attribute, self.key_name
                    ),
                    code=400,
                )
            return jsonify({attribute: self.config.get(self.key_name, attribute)})
        data = {}
        for key in self.config.get_all_childname(self.key_name):
            data[key] = self.config.get(self.key_name, key)
        return jsonify(data)

    @token_required
    def post(self):
        data = request.get_json(force=True)
        for key, value in data.items():
            if not key in self.config.get_all_childname(self.key_name):
                return exception(
                    "Cannot found that attribute {} on {}!".format(key, self.key_name),
                    code=400,
                )
            self.config.set(self.key_name, key, value)
        return jsonify(data)


class SettingsDHCPResource(Resource):
    config = SettingsINI.getInstance()
    key_name = "dhcp"

    @token_required
    def get(self, attribute=None):
        if attribute:
            if not attribute in self.config.get_all_childname(self.key_name):
                return exception(
                    "Cannot found that attribute {} on {}!".format(key, self.key_name),
                    code=400,
                )
            return jsonify({attribute: self.config.get(self.key_name, attribute)})
        data = {}
        for key in self.config.get_all_childname(self.key_name):
            data[key] = self.config.get(self.key_name, key)
        return jsonify(data)

    @token_required
    def post(self):
        data = request.get_json(force=True)
        for key, value in data.items():
            if not key in self.config.get_all_childname(self.key_name):
                return jsonify(
                    {
                        "message": "Cannot found that attribute {} on {}!".format(
                            key, self.key_name
                        )
                    }
                )
            self.config.set(self.key_name, key, value)
        return jsonify(data)


class SettingsAccesspointResource(Resource):
    config = SettingsINI.getInstance()
    key_name = "accesspoint"

    @token_required
    def get(self, attribute=None):
        if attribute:
            if not attribute in self.config.get_all_childname(self.key_name):
                return exception(
                    "Cannot found that attribute {} on {}!".format(
                        attribute, self.key_name
                    ),
                    code=400,
                )
            return jsonify({attribute: self.config.get(self.key_name, attribute)})
        data = {}
        for key in self.config.get_all_childname(self.key_name):
            data[key] = self.config.get(self.key_name, key)
        return jsonify(data)

    @token_required
    def post(self):
        data = request.get_json(force=True)
        for key, value in data.items():
            if not key in self.config.get_all_childname(self.key_name):
                return exception(
                    "Cannot found that attribute {} on {}!".format(key, self.key_name),
                    code=400,
                )
            self.config.set(self.key_name, key, value)
        return jsonify(data)
