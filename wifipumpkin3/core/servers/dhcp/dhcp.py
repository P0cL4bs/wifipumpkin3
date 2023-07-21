import weakref
from re import *
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.component import ComponentBlueprint
from wifipumpkin3.core.common.threads import ProcessThread
from wifipumpkin3.exceptions.errors.dhcpException import (
    DHCPServerSettingsError,
    DHCPdServerNotFound,
)
from wifipumpkin3.core.widgets.default.logger_manager import LoggerManager
from wifipumpkin3.core.lib.mac_vendor_lookup import MacLookup, BaseMacLookup, VendorNotFoundError

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


class DHCPServers(QtCore.QObject, ComponentBlueprint):
    Name = "Generic"
    ID = "Generic"
    haspref = False
    ExecutableFile = ""

    def __init__(self, parent=0):
        super(DHCPServers, self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self._connected = {}
        self.loggermanager = LoggerManager.getInstance()
        self.configure_logger()

    @property
    def DHCPConf(self):
        return self.Settings.updateconf()

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

    def prereq(self):
        dh, gateway = self.DHCPConf["router"], Linux.get_interfaces()["gateway"]
        if gateway != None:
            if (
                dh[: len(dh) - len(dh.split(".").pop())]
                == gateway[: len(gateway) - len(gateway.split(".").pop())]
            ):
                raise DHCPServerSettingsError(
                    "DHCPServer", "dhcp same ip range address "
                )

    def LogOutput(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.logger.info(data)

    def isChecked(self):
        return self.conf.get("accesspoint", self.ID, format=bool)

    def Stop(self):
        self.shutdown()
        self.reactor.stop()
        self._connected = dict()

    def Start(self):
        self.prereq()
        self.Initialize()
        self.boot()

    @property
    def Settings(self):
        return DHCPSettings.instances[0]

    @property
    def commandargs(self):
        pass

    def boot(self):
        print(self.command, self.commandargs)
        self.reactor = ProcessThread({self.command: self.commandargs})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.Name)

    @property
    def command(self):
        cmdpath = os.popen("which {}".format(self.ExecutableFile)).read().split("\n")[0]
        if cmdpath:
            return cmdpath
        raise DHCPdServerNotFound("DHCPServer", "The binary (dhcpd) not found")

    def get_mac_vendor(self, mac):
        """discovery mac vendor by mac address"""
        BaseMacLookup.cache_path = "{}/config/mac-vendors.txt".format(C.user_config_dir)
        mac_obj = MacLookup()
        try:
            d_vendor = mac_obj.lookup(mac)
        except VendorNotFoundError:
            return "unknown vendor"
        return d_vendor 

    def removeInactivityClient(self, mac: str):
        if mac in self._connected:
            self._connected.pop(mac)

    @property
    def getStaClients(self):
        return self._connected

class DHCPSettings(CoreSettings):
    Name = "WP DHCP"
    ID = "DHCP"
    ConfigRoot = "dhcp"
    Category = "DHCP"
    instances = []
    confingDHCP = {}

    def __init__(self, parent=0):
        super(DHCPSettings, self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__

        self.dhmode = [mod(parent) for mod in DHCPServers.__subclasses__()]
        self.updateconf()

    def updateconf(self):
        self.confingDHCP["leasetimeDef"] = self.conf.get(
            self.ConfigRoot, "leasetimeDef"
        )
        self.confingDHCP["leasetimeMax"] = self.conf.get(
            self.ConfigRoot, "leasetimeMax"
        )
        self.confingDHCP["subnet"] = self.conf.get(self.ConfigRoot, "subnet")
        self.confingDHCP["router"] = self.conf.get(self.ConfigRoot, "router")
        self.confingDHCP["netmask"] = self.conf.get(self.ConfigRoot, "netmask")
        self.confingDHCP["broadcast"] = self.conf.get(self.ConfigRoot, "broadcast")
        self.confingDHCP["range"] = self.conf.get(self.ConfigRoot, "range")
        return self.confingDHCP
