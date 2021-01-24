from wifipumpkin3.core.common.threads import ProcessThread
from wifipumpkin3.core.widgets.docks.dock import DockableWidget
from wifipumpkin3.core.controllers.wirelessmodecontroller import AccessPointSettings
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.widgets.default.logger_manager import LoggerManager

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
    def __init__(self, parent):
        Qt.QObject.__init__(self, parent)


class VBox(Qt.QObject):
    def __init__(self):
        Qt.QObject.__init__(self)


class MitmDock(DockableWidget):
    id = "Generic"
    title = "Generic"

    def __init__(self, parent=0, title="", info={}):
        super(MitmDock, self).__init__(parent, title, info)
        self.setObjectName(self.title)


class MitmMode(Widget):
    Name = "Generic"
    ID = "Generic"
    Author = "Wahyudin Aziz"
    Description = "Generic Placeholder for Attack Scenario"
    LogFile = C.LOG_ALL
    CONFIGINI_PATH = ""
    ModSettings = False
    ModType = "proxy"  # proxy or server
    ConfigMitm = None
    Hidden = True
    _cmd_array = []
    plugins = []
    sendError = QtCore.pyqtSignal(str)
    sendSingal_disable = QtCore.pyqtSignal(object)
    config = None
    TypeButton = 1 # 0 for Switch, 1 for Radio

    def __init__(self, parent=None):
        super(MitmMode, self).__init__(parent)
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self.reactor = None
        self.server = None

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

    def parser_set_plugin(self, proxy_name, args):
        # default parser plugin commands complete
        try:
            plugin_name, plugin_status = list(args.split())[1], list(args.split())[2]
            if plugin_status not in ["true", "false", "True", "False"]:
                return print(
                    display_messages(
                        "wifipumpkin3: error: unrecognized arguments {}".format(
                            plugin_status
                        ),
                        error=True,
                    )
                )
            if plugin_name in self.conf.get_all_childname("mitm_modules"):
                return self.conf.set("mitm_modules", plugin_name, plugin_status)
            return print(
                display_messages("plugin {} not found".format(plugin_name), error=True)
            )
        except IndexError as e:
            pass

        print(
            display_messages(
                "unknown sintax command: {}\n".format(proxy_name), error=True
            )
        )

    @property
    def getPlugins(self):
        return None

    @property
    def getConfigINIPath(self):
        return self.CONFIGINI_PATH

    @property
    def getConfig(self):
        return self.config

    def getModType(self):
        return self.ModType

    def setModType(self, type_plugin):
        self.ModType = type_plugin

    def setID(self, id):
        self.ID = id

    def isChecked(self):
        return self.conf.get("mitm_modules", self.ID, format=bool)

    @property
    def CMD_ARRAY(self):
        return self._cmd_array

    @property
    def Wireless(self):
        return AccessPointSettings.instances[0]

    @property
    def hasSettings(self):
        return self.ModSettings

    def Initialize(self):
        self.SetRules()

    def SetRules(self):
        pass

    def ClearRules(self):
        pass

    def Configure(self):
        self.ConfigWindow.show()

    def boot(self):
        if self.CMD_ARRAY:
            self.reactor = ProcessThread({"python": self.CMD_ARRAY})
            self.reactor._ProcssOutput.connect(self.LogOutput)
            self.reactor.setObjectName(self.ID)

    def shutdown(self):
        if self.reactor is not None:
            self.reactor.stop()
            if hasattr(self.reactor, "wait"):
                if not self.reactor.wait(msecs=500):
                    self.reactor.terminate()

    def LogOutput(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.logger.info(data)
