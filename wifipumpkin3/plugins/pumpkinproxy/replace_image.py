from wifipumpkin3.plugins.pumpkinproxy.base import BasePumpkin
from os import path
from io import StringIO

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


class replaceImages(BasePumpkin):
    meta = {
        "_name": "replaceImages",
        "_version": "1.0",
        "_description": "this module proxy replace all images with the picture .",
        "_author": "mh4x0f",
    }

    @staticmethod
    def getName():
        return replaceImages.meta["_name"]

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = True
        self.imagePath = self._config.get("set_replaceImages", "path")

    def handleResponse(self, request, data):
        self.content = request.responseHeaders.getRawHeaders("content-type")
        if str(self.content).startswith("image"):
            if path.isfile(self.imagePath):
                try:
                    img = StringIO(open(self.imagePath, "rb").read().decode())
                    data = img.getvalue()
                    print(
                        "[{}] URL:{} image replaced...".format(self._name, request.uri)
                    )
                except:
                    pass
        return data
