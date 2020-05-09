from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.extensions import *


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


class ExtensionController(ControllerBlueprint):
    ID = "ext_controller"
    ex_handler = {}

    @staticmethod
    def getID():
        return ExtensionController.ID

    def __init__(self, parent):
        super(ExtensionController, self).__init__()
        self.parent = parent
        # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        __manipulator = [
            ext(self.parent.parse_args, self.parent)
            for ext in ExtensionUI.__subclasses__()
        ]
        # save all extension on object dict
        for k in __manipulator:
            self.ex_handler[k.Name] = k
