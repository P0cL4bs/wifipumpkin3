from flask_restful import Resource
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from wifipumpkin3.core.utility.collection import SettingsINI

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


class LoginResource(Resource):
    conf = SettingsINI.getInstance()

    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response(
                "Could not verify",
                401,
                {"WWW-Authenticate": 'Basic realm="Login required!"'},
            )

        admin_password = generate_password_hash(
            self.conf.get("rest_api_settings", "PASSWORD"), method="sha256"
        )
        admin_name = self.conf.get("rest_api_settings", "USERNAME")
        admin_SECRET_KEY = self.conf.get("rest_api_settings", "SECRET_KEY")

        if auth.username != admin_name:
            return make_response(
                "Could not verify",
                401,
                {"WWW-Authenticate": 'Basic realm="Login required!"'},
            )

        admin_public_id = self.conf.get("rest_api_settings", "public_id")

        if check_password_hash(admin_password, auth.password):
            token = jwt.encode(
                {
                    "public_id": admin_public_id,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=3000),
                },
                admin_SECRET_KEY,
            )

            return jsonify({"token": token.decode("UTF-8")})

        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )
