from scapy.all import *
from wifipumpkin3.plugins.sniffkin3.default import PSniffer
from string import ascii_letters

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


class ImageCap(PSniffer):
    """ capture image content http"""

    _activated = False
    _instance = None
    meta = {
        "Name": "imageCap",
        "Version": "1.0",
        "Description": "capture image content http",
        "Author": "Pumpkin-Dev",
    }

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value

    @staticmethod
    def getInstance():
        if ImageCap._instance is None:
            ImageCap._instance = ImageCap()
        return ImageCap._instance

    def filterPackets(self, pkt):
        pass

    def random_char(self, y):
        return "".join(random.choice(ascii_letters) for x in range(y))
