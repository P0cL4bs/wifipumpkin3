import weakref
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.widgets.default import *

from wifipumpkin3.core.controllers.wirelessmodecontroller import *
from wifipumpkin3.core.controllers.dhcpcontroller import *
from wifipumpkin3.core.controllers.proxycontroller import *
from wifipumpkin3.core.controllers.mitmcontroller import *
from wifipumpkin3.core.controllers.dnscontroller import *
from wifipumpkin3.core.controllers.uicontroller import *
from wifipumpkin3.core.controllers.extensioncontroller import *

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


class DefaultController(Qt.QObject):

    _controllers = {}
    instances = []

    def __init__(self, parent=None, **kwargs):
        super(DefaultController, self).__init__()
        self.__class__.instances.append(weakref.proxy(self))
        self.parent = parent
        self.FSettings = SuperSettings.getInstance()
        self.defaultui = []
        self.allui = []
        self.__tabbyname = {}
        # load all pluginsUI class
        __defaultui = [ui(parent, self.FSettings) for ui in TabsWidget.__subclasses__()]
        for ui in __defaultui:
            if not ui.isSubitem:
                self.defaultui.append(ui)
            self.allui.append(ui)
            self.__tabbyname[ui.Name] = ui
            setattr(self.__class__, ui.ID, ui)

        self.intialize_controllers(self.parent)

    def intialize_controllers(self, parent):
        """ initialize all controllers"""
        WirelessModeController(parent)
        DHCPController(parent)
        DNSController(parent)
        UIController(parent)
        ExtensionController(parent)

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    def addController(self, instance):
        """ add controller instance app """
        self._controllers[instance.getID()] = instance

    def getController(self, name):
        """ get controller instance app """
        if name:
            return self._controllers.get(name)
        return self._controllers

    def CoreTabsByName(self, name):

        if self.__tabbyname.has_key(name):
            return self.__tabbyname[name]

    @property
    def CoreTabs(self):
        return self.defaultui
