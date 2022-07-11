from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
from flask_restful import Resource
from flask import jsonify, request
import os, json
from itertools import islice
from wifipumpkin3.core.servers.rest.ext.auth import token_required
from wifipumpkin3.core.servers.rest.ext.exceptions import exception
from datetime import datetime
import urllib.parse

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


class getAllFileLogResource(Resource):
    config = SettingsINI.getInstance()
    args = ("page", "session", "excludes")
    exludes_logs = []
    filenames = (
        "pumpkin_proxy",
        "pydns_server",
        "pydhcp_server",
        "sniffkin3",
        "captiveportal",
        "responder3",
    )
    limit_view = 10
    session = None

    def chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def parser_data(self, list_data: list, session):
        resp_list = []
        for line in list_data:
            resp_data = {}
            if line["record"]["extra"]["session"] == session:
                resp_data["time"] = str(
                    datetime.fromtimestamp(line["record"]["time"]["timestamp"]).replace(
                        microsecond=0
                    )
                )
                resp_data["timestamp"] = line["record"]["time"]["timestamp"]
                resp_data["message"] = line["record"]["message"]
                resp_data["text"] = line["text"]
                resp_data["name"] = line["record"]["extra"]["name"]
                resp_data["session"] = line["record"]["extra"]["session"]
                resp_list.append(resp_data)

        return sorted(
            resp_list, key=lambda x: datetime.strptime(x["time"], "%Y-%m-%d %H:%M:%S")
        )

    @token_required
    def get(self):
        for args in request.args:
            if not args in self.args:
                return exception(
                    "Cannot found parameters {} on request ".format(args), code=400
                )

        table = []
        page = int(request.args.get("page"))
        if request.args.get("excludes"):
            resq_exclude = urllib.parse.unquote_plus(request.args.get("excludes"))
            self.exludes_logs = tuple(x.strip() for x in resq_exclude.split(","))

        if request.args.get("session"):
            self.session = request.args.get("session")

        for filename in self.filenames:
            if (
                os.path.isfile("{}/{}.log".format(C.LOG_BASE, filename))
                and filename not in self.exludes_logs
            ):
                with open("{}/{}.log".format(C.LOG_BASE, filename), "r") as f:
                    for line in f:
                        table.append(json.loads(line))

        table = self.parser_data(table, self.session)
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
