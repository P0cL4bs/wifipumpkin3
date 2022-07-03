from wifipumpkin3.core.servers.mitm.mitmmode import MitmMode
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.widgets.docks.dock import DockableWidget
from wifipumpkin3.core.common.threads import ProcessThread
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


class NetCredential(DockableWidget):
    id = "Responder"
    title = "Responder"

    def __init__(self, parent=None, title="", info={}):
        super(NetCredential, self).__init__(parent, title, info)
        self.setObjectName(self.title)

    def writeModeData(self, data):
        """get data output and add on QtableWidgets"""
        print(data)
        # self.THeaders['Username'].append(data['POSTCreds']['User'])
        # self.THeaders['Password'].append(data['POSTCreds']['Pass'])
        # self.THeaders['Url'].append(data['POSTCreds']['Url'])
        # self.THeaders['Source/Destination'].append(data['POSTCreds']['Destination'])

    def stopProcess(self):
        pass


class Responder(MitmMode):
    Name = "Responder"
    ID = "responder"
    Author = "PumpkinDev"
    Description = "LLMNR, NBT-NS and MDNS poisoner, with built-in HTTP/SMB/MSSQL/FTP/LDAP rogue authentication server "
    LogFile = C.LOG_RESPONDER
    Hidden = False
    ConfigMitmPath = None
    _cmd_array = []
    ModSettings = True
    ModType = "server"  # proxy or server
    config = None
    TypeButton = 0  # 0 for Switch, 1 for Radio
    Binary_exec = "responder"

    def __init__(self, parent, FSettingsUI=None, main_method=None, **kwargs):
        super(Responder, self).__init__(parent)
        self.setID(self.ID)
        self.setModType(self.ModType)
        self.dockwidget = NetCredential(None, title=self.Name)

    @property
    def CMD_ARRAY(self):
        iface = self.conf.get("accesspoint", "interface")
        self._cmd_array = ["-I", iface, "-wd"]
        return self._cmd_array

    def boot(self):
        binary_path = self.getBinaryExecPath
        if binary_path:
            self.reactor = ProcessThread({binary_path: self.CMD_ARRAY})
            self.reactor._ProcssOutput.connect(self.LogOutput)
            return self.reactor.setObjectName(self.ID)
        print(
            display_messages(
                "command not found: {}".format(self.Binary_exec), error=True
            )
        )

    def parser_set_responder(self, status, plugin_name):
        try:
            # plugin_name = pumpkinproxy.no-cache
            name_plugin, key_plugin = (
                plugin_name.split(".")[0],
                plugin_name.split(".")[1],
            )
            if key_plugin in self.config.get_all_childname("plugins"):
                self.config.set("plugins", key_plugin, status)
                print(
                    display_messages(
                        "responder: {} status: {}".format(key_plugin, status),
                        sucess=True,
                    )
                )
            else:
                print(
                    display_messages(
                        "unknown plugin: {}".format(key_plugin), error=True
                    )
                )
        except IndexError:
            print(display_messages("unknown sintax command", error=True))
