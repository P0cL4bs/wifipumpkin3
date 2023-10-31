from wifipumpkin3.core.common.threads import ProcessThread
from wifipumpkin3.core.controllers.wirelessmodecontroller import AccessPointSettings
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.widgets.docks.dock import *
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.widgets.default.logger_manager import LoggerManager
from wifipumpkin3.core.utility.component import ComponentBlueprint

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


class Widget(Qt.QObject):
    def __init__(self):
        Qt.QObject.__init__(self)

class ProxyMode(Widget, ComponentBlueprint):
    Name = "Generic"
    Author = "Wahyudin Aziz"
    ID = "generic"
    Description = "Generic Placeholder for Attack Scenario"
    LogFile = C.LOG_ALL
    CONFIGINI_PATH = ""
    ModSettings = False
    ModType = "proxy"  # proxy or server
    EXEC_PATH = ""
    _cmd_array = []
    Hidden = True
    plugins = []
    sendError = QtCore.pyqtSignal(str)
    sendSingal_disable = QtCore.pyqtSignal(object)
    addDock = QtCore.pyqtSignal(object)
    TypePlugin = 1
    RunningPort = 80
    config = None

    def __init__(self, parent):
        super(ProxyMode, self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()

        self.handler = None
        self.reactor = None
        self.subreactor = None
        self.defaults_rules = {}
        self.defaults_rules[self.ID] = []
        # set config path plugin
        if self.getConfigINIPath != "":
            self.config = SettingsINI(self.getConfigINIPath)

        self.loggermanager = LoggerManager.getInstance()
        self.configure_logger()

    def configure_logger(self):
        if not self.Hidden:
            config_extra = self.loggermanager.getExtraConfig(self.ID)
            config_extra["extra"]["session"] = self.parent.currentSessionID

            self.logger = StandardLog(
                self.ID,
                colorize=self.conf.get("settings", "log_colorize", format=bool),
                serialize=self.conf.get("settings", "log_serialize", format=bool),
                config=config_extra,
            )
            self.logger.filename = self.LogFile
            self.loggermanager.add(self.ID, self.logger)

    def parser_set_proxy(self, proxy_name, *args):
        # default parser proxy commands complete
        if not self.conf.get("accesspoint", "status_ap", format=bool):
            plugins_selected = [
                plugin
                for plugin in self.conf.get_all_childname("proxy_plugins")
                if plugin == proxy_name
            ]
            if plugins_selected != []:
                self.conf.set("proxy_plugins", plugins_selected[0], True)
                for proxy in self.conf.get_all_childname("proxy_plugins"):
                    if proxy != plugins_selected[0] and not "_config" in proxy:
                        self.conf.set("proxy_plugins", proxy, False)
                return
            return print(
                display_messages("unknown command: {} ".format(proxy_name), error=True)
            )
        print(
            display_messages(
                "Error: 0x01 - the AP(access point) is running", error=True
            )
        )

    def runDefaultRules(self):
        for rules in self.defaults_rules[self.ID]:
            os.system(rules)

    @property
    def getPlugins(self):
        return None

    @property
    def getConfigINIPath(self):
        return self.CONFIGINI_PATH

    @property
    def getConfig(self):
        return self.config

    def add_default_rules(self, rule: str):
        self.defaults_rules[self.ID].append(rule)

    def setRunningPort(self, value):
        self.RunningPort = value

    def getRunningPort(self):
        if self.config:
            return self.config.get("settings", "proxy_port")
        return self.RunningPort

    def getTypePlugin(self):
        return self.TypePlugin

    def setTypePlugin(self, type_plugin):
        self.TypePlugin = type_plugin

    def setID(self, id):
        self.ID = id

    def isChecked(self):
        return self.conf.get("proxy_plugins", self.ID, format=bool)

    @property
    def getIptablesPath(self):
        return self.conf.get("iptables", "path_binary")

    @property
    def iptablesrules(self):
        pass

    @property
    def Wireless(self):
        return AccessPointSettings.instances[0]

    def onProxyEnabled(self):
        pass

    def onProxyDisabled(self):
        pass

    @property
    def hasSettings(self):
        return self.ModSettings

    @property
    def CMD_ARRAY(self):
        # self._cmd_array.extend(self.parent.currentSessionID)
        return self._cmd_array

    def boot(self):
        self.reactor = ProcessThread({"python3": self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

    def shutdown(self):
        if self.reactor is not None:
            self.reactor.stop()
            if hasattr(self.reactor, "wait"):
                if not self.reactor.wait(msecs=500):
                    self.reactor.terminate()

    @property
    def isEnabled(self):
        pass

    def Initialize(self):
        pass

    def optionsRules(self, type):
        """add rules iptable by type plugins"""
        return self.search[type]

    def ClearRules(self):
        for rules in self.search.keys():
            self.unset_Rules(rules)

    def LogOutput(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            print(data)

    def Configure(self):
        self.ConfigWindow.show()

    def SaveLog(self):
        pass

    def Serve(self, on=True):
        pass


class Dockable(DockableWidget):
    def __init__(self, parent=0, title="", info={}):
        super(Dockable, self).__init__(parent, title, info)
        self.setObjectName(title)
