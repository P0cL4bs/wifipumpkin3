import weakref
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.component import ComponentBlueprint
from wifipumpkin3.core.common.threads import ProcessThread
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


class DNSBase(QtCore.QObject, ComponentBlueprint):
    Name = "DNSBaseClass"
    ID = "DNSBase"
    Author = "Dev"
    ConfigRoot = "DNSServer"
    ExecutableFile = ""
    LogFile = ""
    hasPreference = False
    arguments = [
        ["label", "switch", "type", "defaultvalue", "enabled", "required"],
    ]

    addDock = QtCore.pyqtSignal(object)

    def __init__(self, parent, **kwargs):
        super(DNSBase, self).__init__(parent)
        self.parent = parent
        self.conf = SuperSettings.getInstance()

        self.reactor = None
        self.loggermanager = LoggerManager.getInstance()
        self.configure_logger()

    def configure_logger(self):
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

    def isChecked(self):
        return self.conf.get("accesspoint", self.ID, format=bool)

    @property
    def commandargs(self):
        pass

    @property
    def command(self):
        cmdpath = os.popen("which {}".format(self.ExecutableFile)).read().split("\n")[0]
        if cmdpath:
            return cmdpath
        else:
            return None

    def boot(self):
        self.reactor = ProcessThread({self.command: self.commandargs})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

    def LogOutput(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.logger.info(data)


class DNSSettings(CoreSettings):
    Name = "DNS Server"
    ID = "DNSSettings"
    Category = "DNS"
    instances = []

    def __init__(self, parent=None):
        super(DNSSettings, self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__

        self.dnslist = [dns(self.parent) for dns in DNSBase.__subclasses__()]

    @classmethod
    def getInstance(cls):
        return cls.instances[0]
