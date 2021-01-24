from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
from flask_restful import Resource
from flask import jsonify, request
import os, json
from itertools import islice
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


class getFileLogResource(Resource):
    config = SettingsINI.getInstance()
    args = "page"
    limit_view = 10

    def chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    @token_required
    def get(self, filename=None):
        if not os.path.isfile("{}/{}.log".format(C.LOG_BASE, filename)):
            return exception("Cannot found that file log {}".format(filename), code=400)
        for args in request.args:
            if not args in self.args:
                return exception(
                    "Cannot found parameters {} on request ".format(args), code=400
                )

        table = []
        page = int(request.args.get("page"))
        with open("{}/{}.log".format(C.LOG_BASE, filename), "r") as f:
            for line in f:
                table.append(json.loads(line))
        data_splited = list(self.chunk(table, self.limit_view))

        if page <= (len(data_splited) - 1):
            return jsonify(
                {
                    "data": {
                        "items": data_splited[page],
                        "limit_view": self.limit_view,
                        "total_pages": (len(table) // self.limit_view) + 1,
                        "current_page": page,
                        "total_count": len(table),
                    }
                }
            )
        return jsonify(
            {
                "data": {
                    "items": [],
                    "limt_view": self.limit_view,
                    "total_pages": (len(table) // self.limit_view) + 1,
                    "current_page": page,
                    "total_count": len(table),
                }
            }
        )

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
