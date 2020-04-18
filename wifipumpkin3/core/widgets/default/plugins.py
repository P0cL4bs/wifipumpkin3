from wifipumpkin3.core.common.uimodel import *
from PyQt5.QtCore import pyqtSignal

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


class Plugins(TabsWidget):
    Name = "Plugins"
    ID = "Plugins"
    __subitem = False
    sendSingal_disable = pyqtSignal(object)

    def __init__(self, parent, FSettings=None):
        super(Plugins, self).__init__(parent, FSettings)
        self.__plugins = [plug(parent) for plug in PluginsUI.__subclasses__()]
        for wid in self.__plugins:
            setattr(self, wid.ID, wid)
