from flask import Flask
from wifipumpkin3.core.servers.rest.ext import configuration

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


class RestControllerAPI(object):
    def __init__(self, name, config):
        self.conf = config
        self.app = Flask(name)
        self.port_rest = self.conf.get("rest_api_settings", "port")
        configuration.init_app(self.app, self.conf)
        configuration.load_extensions(self.app)

    def run(self):
        self.app.run(debug=False, port=self.port_rest)
