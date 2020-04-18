from os import path
from PyQt5.QtCore import QSettings
import wifipumpkin3.core.utility.constants as C

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


class SettingsINI(object):
    """ settings INI file implemented for Wifi-Pumpkin"""

    _instance = None

    def __init__(self, filename):
        if path.isfile(filename):
            self.psettings = QSettings(filename, QSettings.IniFormat)

    @staticmethod
    def getInstance():
        if SettingsINI._instance is None:
            SettingsINI._instance = SettingsINI(C.CONFIG_INI)
        return SettingsINI._instance

    def get(self, name_group, key, format=str):
        """ Get the value for setting key """
        self.psettings.beginGroup(name_group)
        value = self.psettings.value(key, type=format)
        self.closeGroup()
        return value

    def set(self, name_group, key, value):
        """ Sets the value of setting key to value """
        self.psettings.beginGroup(name_group)
        self.psettings.setValue(key, value)
        self.closeGroup()

    def set_one(self, name_group, key, value):
        """ Sets the value of setting key to value """
        self.set(name_group, key, value)
        for item in self.get_all_childname(name_group):
            if item != key:
                self.set(name_group, item, False)

    def get_by_index_key(self, index, key=str):
        """ get specific key value by index type(list) """
        return str(self.get(key, self.get_all_childname(key)[index]))

    def get_all_childname(self, key):
        """ get list all childskeys on file config.ini """
        return [x.split("/")[1] for x in self.get_all_keys() if x.split("/")[0] == key]

    def get_name_activated_plugin(self, key):
        """ get status by plugin name """
        plugins = self.get_all_childname(key)
        for plugin in plugins:
            if self.get(key, plugin, format=bool):
                return plugin
        return None

    def get_all_keys(self):
        """ get all keys on settings"""
        return self.psettings.allKeys()

    def closeGroup(self):
        """ close group settings"""
        self.psettings.endGroup()
