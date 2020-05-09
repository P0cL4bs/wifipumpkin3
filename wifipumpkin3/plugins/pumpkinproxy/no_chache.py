from wifipumpkin3.plugins.pumpkinproxy.base import BasePumpkin

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


class nocache(BasePumpkin):
    meta = {
        "_name": "no-cache",
        "_version": "1.0",
        "_description": "disable browser caching, cache-control in HTML",
        "_author": "mh4x0f",
    }

    @staticmethod
    def getName():
        return nocache.meta["_name"]

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = False

    def handleHeader(self, request, key, value):
        if key.decode().lower() == "cache-control":
            value = "no-cache".encode()

        if key.decode().lower() == "if-none-match":
            value = "".encode()
        if key.decode().lower() == "etag":
            value = "".encode()
