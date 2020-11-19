from wifipumpkin3.core.servers.rest.ext import auth
from wifipumpkin3.core.servers.rest.blueprints import restapi
from wifipumpkin3.core.utility.collection import SettingsINI
import uuid

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


def load_extensions(app):
    auth.init_app(app)
    restapi.init_app(app)


def secretkey_generate():
    return str(uuid.uuid4())


def init_app(app, config):
    conf = SettingsINI.getInstance()
    secret_key = secretkey_generate()
    conf.set("rest_api_settings", "SECRET_KEY", secret_key)
    app.config.update(TESTING=False, SECRET_KEY=secret_key)
