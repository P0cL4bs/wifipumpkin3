from wifipumpkin3.core.config.globalimport import *
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.common.platforms import Linux

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


class CoreSettings(Linux):

    Name = "General"
    ID = "General"
    ConfigRoot = "General"
    Category = "General"
    Icon = None
    __subitem = False
    conf = {}

    def __init__(self, parent=0, FSettings=None):
        super(CoreSettings, self).__init__()
        self.parent = parent
        self.conf = SettingsINI(C.CONFIG_INI)

    def deleteObject(self, obj):
        """ reclaim memory """
        del obj

    @property
    def getIptablesPath(self):
        return self.conf.get("iptables", "path_binary")

    @property
    def isSubitem(self):
        return self.__subitem

    def osWalkCallback(self, arg, directory, files):
        pass


class TabsWidget(Qt.QObject):
    Name = "Generic"
    ID = "Generic"
    Icon = ""
    __subitem = False

    def __init__(self, parent=0, FSettings=None):
        super(TabsWidget, self).__init__()
        self.setObjectName(self.Name)
        self.conf = SuperSettings.getInstance()
        self.parent = parent

    @property
    def isSubitem(self):
        return self.__subitem


class PluginsUI(Qt.QObject):
    Name = "Default"
    Caption = "Default"
    ID = "Generic"

    def __init__(self, parent=0):
        super(PluginsUI, self).__init__(parent)
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self.sessionconfig = {}

    @property
    def config(self):
        return self.sessionconfigcd

    def deleteObject(self, obj):
        del obj
