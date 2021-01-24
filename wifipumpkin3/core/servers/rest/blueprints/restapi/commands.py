from flask import jsonify, request
from wifipumpkin3 import PumpkinShell
from flask_restful import Resource
from io import StringIO
import sys
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


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class CommandsResource(Resource):
    def __init__(self):
        self.root = PumpkinShell.getInstance()
        super(CommandsResource, self).__init__()

    @token_required
    def get(self, command=None):
        output = []
        with Capturing(output) as output:
            self.root.onecmd(command)
        return jsonify(output)


class CommandsPostResource(Resource):
    def __init__(self):
        self.root = PumpkinShell.getInstance()
        super(CommandsPostResource, self).__init__()

    @token_required
    def post(self, command=None):
        data = request.get_json(force=True)
        if not "commands" in data:
            return exception(
                "Cannot found that key commands  on data",
                code=400,
            )
        output = []
        with Capturing(output) as output:
            self.root.onecmd(data.get("commands"))
        return jsonify(output)