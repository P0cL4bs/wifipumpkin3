from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.servers.dhcp import *
from wifipumpkin3.core.ui import *

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


class UIController(ControllerBlueprint):
    ID = "ui_controller"
    ui_handler = {}

    @staticmethod
    def getID():
        return UIController.ID

    def __init__(self, parent):
        super(UIController, self).__init__()
        self.parent = parent
        # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        __manipulator = [
            prox(parent=self.parent) for prox in uimode.WidgetBase.__subclasses__()
        ]

        for k in __manipulator:
            self.ui_handler[k.Name] = k

        # set all ui plugin as child class
        for n, p in self.ui_handler.items():
            setattr(self, p.ID, p)
