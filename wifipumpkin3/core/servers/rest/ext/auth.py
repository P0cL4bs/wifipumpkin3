from wifipumpkin3.core.utility.collection import SettingsINI
import uuid
from flask import request, jsonify, make_response
import jwt
from functools import wraps

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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return make_response(
                jsonify({"message": "Token is invalid!"}),
                401
            )
        conf = SettingsINI.getInstance()

        try:
            app_secret_key = conf.get("rest_api_settings", "SECRET_KEY")
            data = jwt.decode(token, app_secret_key)
            app_public_id = conf.get("rest_api_settings", "public_id")
            if app_public_id != data["public_id"]:
                return make_response(
                jsonify({"message": "Token is invalid!"}),
                401
            )
        except:
            return make_response(
                jsonify({"message": "Token is invalid!"}),
                401
            )

        return f(*args, **kwargs)

    return decorated


def init_app(app):
    conf = SettingsINI.getInstance()
    conf.set("rest_api_settings", "public_id", str(uuid.uuid4()))
