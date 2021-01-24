from flask import Blueprint
from flask_restful import Api
import wifipumpkin3.core.servers.rest.blueprints.restapi.accesspoint as res_ap
import wifipumpkin3.core.servers.rest.blueprints.restapi.authenticate as res_auth
import wifipumpkin3.core.servers.rest.blueprints.restapi.logger as res_logger
import wifipumpkin3.core.servers.rest.blueprints.restapi.plugins as res_plugins
import wifipumpkin3.core.servers.rest.blueprints.restapi.proxies as res_proxies
import wifipumpkin3.core.servers.rest.blueprints.restapi.commands as res_command

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


bp = Blueprint("wp3 Rest API", __name__, url_prefix="/api/v1")
api = Api(bp)


def init_app(app):

    api.add_resource(res_auth.LoginResource, "/authenticate/")
    api.add_resource(res_logger.getFileLogResource, "/logger/<string:filename>")

    api.add_resource(
        res_ap.SettingsAccesspointResource,
        "/config/accesspoint",
        "/config/accesspoint/<string:attribute>",
    )
    api.add_resource(
        res_ap.SettingsDHCPResource, "/config/dhcp", "/config/dhcp/<string:attribute>"
    )

    api.add_resource(
        res_ap.SettingsAPmodeResource, "/apmode", "/apmode/<string:attribute>"
    )

    api.add_resource(res_ap.ClientsResource, "/clients")

    api.add_resource(
        res_plugins.SettingsPluginResource, "/plugins", "/plugins/<string:attribute>"
    )
    api.add_resource(res_plugins.MitmPluginsResource, "/plugins/info")

    api.add_resource(
        res_plugins.PluginsInfoResource, "/plugins", "/plugins/<string:plugin_name>/info"
    )

    api.add_resource(
        res_proxies.SettingsProxyResource, "/proxies", "/proxies/<string:attribute>"
    )

    api.add_resource(
        res_proxies.ProxiesInfoResource, "/proxies", "/proxies/<string:proxy_name>/info"
    )
    api.add_resource(
        res_proxies.ProxiesAllInfoResource, "/proxies", "/proxies/info"
    )

    api.add_resource(res_plugins.SettingsPluginsResource, "/<string:plugin_id>/plugins")

    api.add_resource(res_command.CommandsResource, "/commands/<string:command>")
    api.add_resource(res_command.CommandsPostResource, "/commands")

    app.register_blueprint(bp)
