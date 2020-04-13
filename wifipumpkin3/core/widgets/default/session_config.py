from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
import weakref

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


class SessionConfig(TabsWidget):
    ConfigRoot = "Settings"
    Name = "Settings"
    ID = "SessionConfig"
    __subitem = False
    tablayout = {}
    tabwidget = {}
    instances = []

    def __init__(self, parent=None, FSettings=None):
        super(SessionConfig, self).__init__(parent, FSettings)
        self.__class__.instances.append(weakref.proxy(self))
        self.FSettings = SuperSettings.getInstance()
        self.title = self.__class__.__name__

        settingsItem = [
            setitem(self.parent) for setitem in CoreSettings.__subclasses__()
        ]
        self.settingsItem = {}

        for mod in settingsItem:
            self.settingsItem[mod.title] = mod
            setattr(self.__class__, mod.ID, mod)

    @property
    def isSubitem(self):
        return self.__subitem

    @classmethod
    def getInstance(cls):
        return cls.instances[0]
