from wifipumpkin3.core.config.globalimport import *
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.servers.proxy.proxymode import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.plugins.captiveflask import *
from ast import literal_eval

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

class CaptivePortal(ProxyMode):
    Name = "Captive Portal"
    Author = "Pumpkin-Dev"
    ID = "captiveflask"
    Description = (
        "Allow block Internet access for users until they open the page login page."
    )
    Hidden = False
    LogFile = C.LOG_CAPTIVEPO
    CONFIGINI_PATH = C.CONFIG_CP_INI
    _cmd_array = []
    ModSettings = True
    RunningPort = 80
    ModType = "proxy"
    TypePlugin = 1
    TypeButton = 1  # 0 for Switch, 1 for Radio

    def __init__(self, parent=None, **kwargs):
        super(CaptivePortal, self).__init__(parent)
        self.setID(self.ID)
        self.setTypePlugin(self.TypePlugin)
        self.plugins = []
        self.search_all_ProxyPlugins()

    @property
    def CMD_ARRAY(self):
        self.tamplate = self.getPluginActivated()
        self._cmd_array = [
            "-t",
            self.tamplate.TemplatePath,
            "-r",
            self.conf.get("dhcp", "router"),
            "-s",
            self.tamplate.StaticPath,
            "-f",
            self.config.get("settings", "force_redirect_sucessful_template"),
            "-rU",
            self.config.get("settings", "force_redirect_to_url"),
            "-p",
            self.config.get("settings", "proxy_port"),
        ]
        return self._cmd_array

    def Initialize(self):
        # settings iptables for add support captive portal
        IFACE = self.conf.get("accesspoint", "interface")
        IP_ADDRESS = self.conf.get("dhcp", "router")
        PORT = self.config.get("settings", "proxy_port")

        print(display_messages("settings for captive portal:", info=True))
        print(display_messages("allow FORWARD UDP DNS", info=True))
        self.add_default_rules(
            "{iptables} -A FORWARD -i {iface} -p tcp --dport 53 -j ACCEPT".format(
                iptables=self.getIptablesPath, iface=IFACE
            )
        )
        
        print(display_messages("allow traffic to captive portal", info=True))
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
        
        if self.config.get("settings", "force_redirect_https_connection", format=bool):
            print(display_messages("redirecting HTTPS traffic to captive portal", info=True))
            self.add_default_rules(
                "{iptables} -t nat -A PREROUTING -i {iface} -p tcp --dport 443 -j DNAT --to-destination {ip}:{port}".format(
                    iptables=self.getIptablesPath, iface=IFACE, ip=IP_ADDRESS, port=PORT
                )
            )
            
        self.runDefaultRules()

    def boot(self):
        self.reactor = ProcessThread({"captiveflask": self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

    @property
    def getPlugins(self):
        commands = self.config.get_all_childname("plugins")
        list_commands = []
        for command in commands:
            list_commands.append(self.ID + "." + command)
            for sub_plugin in self.config.get_all_childname("set_{}".format(command)):
                list_commands.append("{}.{}.{}".format(self.ID, command, sub_plugin))
        # load all settings extra plugin
        settings = self.config.get_all_childname("settings")
        for config in settings:
            list_commands.append("{}.{}".format(self.ID, config))

        return list_commands

    def LogOutput(self, data):
        headers_table, output_table = ["IP", "Login", "Password"], []
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.logger.info(data)
            try:
                data = literal_eval(data)
                ip = list(data.keys())[0]
                output_table.append(
                    [
                        ip,
                        setcolor(data[ip]["login"], "red"),
                        setcolor(data[ip]["password"], "red"),
                    ]
                )
                print(
                    display_messages(
                        "CaptiveFlask credentials:", info=True, sublime=True
                    )
                )
                return display_tabulate(headers_table, output_table)
            except SyntaxError:
                pass

    def parser_set_captiveflask(self, status, plugin_name):
        if len(plugin_name.split()[0].split(".")) == 2:
            try:
                # plugin_name = captiveflask.FlaskDemo.En true
                name_plugin, key_plugin = (
                    plugin_name.split(".")[0],
                    plugin_name.split(".")[1].split()[0],
                )
                if key_plugin in self.config.get_all_childname("plugins"):
                    self.setPluginActivated(key_plugin, status)
                elif key_plugin in self.config.get_all_childname("settings"):
                    self.config.set("settings", key_plugin, status)
                else:
                    print(
                        display_messages(
                            "unknown plugin: {}".format(key_plugin), error=True
                        )
                    )
            except IndexError:
                print(display_messages("unknown sintax command", error=True))
        elif len(plugin_name.split()[0].split(".")) == 3:
            try:
                # plugin_name = captiveflask.FlaskDemo.En true
                name_plugin, key_plugin = (
                    plugin_name.split(".")[1],
                    plugin_name.split(".")[2].split()[0],
                )
                if key_plugin in self.config.get_all_childname(
                    "set_{}".format(name_plugin)
                ):
                    # self.config.set("set_{}".format(name_plugin), key_plugin, status)
                    self.setSubPluginActivated(name_plugin, key_plugin, status)
                else:
                    print(
                        display_messages(
                            "unknown plugin: {}".format(key_plugin), error=True
                        )
                    )
            except IndexError:
                print(display_messages("unknown sintax command", error=True))

    def search_all_ProxyPlugins(self):
        """load all plugins function"""
        plugin_classes = plugin.CaptiveTemplatePlugin.__subclasses__()
        for p in plugin_classes:
            self.plugins.append(p())

    def setPluginActivated(self, key, status):
        self.config.set("plugins", key, status)
        plugins = self.config.get_all_childname("plugins")
        for plugin in plugins:
            if plugin != key:
                self.config.set("plugins", plugin, False)

    def setSubPluginActivated(self, plugin, key, status):
        self.config.set("set_{}".format(plugin), key, status)
        plugins = self.config.get_all_childname("set_{}".format(plugin))
        for plu in plugins:
            if plu != key:
                self.config.set("set_{}".format(plugin), plu, False)

    def getPluginActivated(self):
        for plugin in self.plugins:
            if self.config.get("plugins", plugin.Name, format=bool):
                self.plugin_activated = plugin
        self.plugin_activated.initialize()  # change language if exist
        return self.plugin_activated
