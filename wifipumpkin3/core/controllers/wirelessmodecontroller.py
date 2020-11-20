import weakref
from wifipumpkin3.core.config.globalimport import *
from os import path, mkdir
from shutil import move
from wifipumpkin3.core.wirelessmode import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.wirelessmode import *
from wifipumpkin3.core.utility.component import ControllerBlueprint

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


class WirelessModeController(ControllerBlueprint):
    ID = "wireless_controller"

    @staticmethod
    def getID():
        return WirelessModeController.ID

    def __init__(self, parent, **kwargs):
        super(WirelessModeController, self).__init__()
        self.parent = parent
        # self.setHidden(True) # hide widget on home
        self.conf = SettingsINI.getInstance()
        # append controller in DefaultWidget
        self.parent.getDefault.addController(self)

    @property
    def Activated(self):
        return self.Settings.getActiveMode

    def getInfo(self):
        return self.Settings.getModesInfo

    @property
    def ActiveReactor(self):
        return self.Settings.getActiveMode.reactor

    def getReactorInfo(self):
        info_reactor = {}
        info_reactor[self.ActiveReactor.getID()] = {
            "ID": self.ActiveReactor.getID(),
            "PID": self.ActiveReactor.getpid(),
        }
        return info_reactor

    @property
    def Settings(self):
        return AccessPointSettings.instances[0]

    def Start(self):
        """ start Access Point and settings plugins  """
        # if not type(self.Activated.get_soft_dependencies()) is bool: return

        self.Activated.Start()
        return None

    def Stop(self):
        pass


class AccessPointSettings(CoreSettings):
    Name = "Access Point"
    ID = "Wireless"
    Category = "Wireless"
    instances = []

    def __init__(self, parent):
        super(AccessPointSettings, self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__

        # load all mode wireless
        self.__modelist = [
            mode(self.parent) for mode in wirelessmode.Mode.__subclasses__()
        ]

    def ModelistChanged(self, mode, widget):
        pass

    @property
    def getActiveMode(self):
        """ get mode activated from settings file """
        for mode in self.__modelist:
            if mode.isChecked():
                return mode

    @property
    def getModesInfo(self):
        mode_info = {}
        for mode in self.__modelist:
            mode_info[mode.ID] = {
                "Name": mode.Name,
                "Checked": mode.isChecked(),
                "ID": mode.ID,
            }
        return mode_info

    @property
    def getInstances(self):
        return self.instances

    def parser_set_mode(self, mode_name, *args):
        # default parser mode commands complete
        if mode_name in self.conf.get_all_childname("ap_mode"):
            mode_selected = self.conf.get_name_activated_plugin("ap_mode")
            if mode_selected != None:
                self.conf.set("ap_mode", mode_name, True)
                for mode in self.conf.get_all_childname("ap_mode"):
                    if mode != mode_name:
                        self.conf.set("ap_mode", mode, False)
                return
        return print(
            display_messages("unknown command: {} ".format(mode_name), error=True)
        )

    @property
    def getCommands(self):
        commands = ["wpa_algorithms", "wpa_sharedkey", "wpa_type"]
        list_commands = []
        for command in commands:
            list_commands.append("security" + "." + command)
        return list_commands

    def parser_set_security(self, value, settings):
        try:
            # key = security.wpa_sharedkey
            name, key = settings.split(".")[0], settings.split(".")[1]
            if key in self.conf.get_all_childname("accesspoint"):
                return self.conf.set("accesspoint", key, value)
            print(display_messages("unknown flag: {}".format(key), error=True))
        except IndexError:
            print(display_messages("unknown sintax command", error=True))

    def configure_network_AP(self):
        """ configure interface and dhcpd for mount Access Point """
        self.DHCP = self.Settings.DHCP.conf
        self.SettingsEnable["PortRedirect"] = self.settings.get_setting(
            "settings", "redirect_port"
        )
        self.SettingsAP = {
            "interface": [
                "ifconfig %s up" % (self.SettingsEnable["AP_iface"]),
                "ifconfig %s %s netmask %s"
                % (
                    self.SettingsEnable["AP_iface"],
                    self.DHCP["router"],
                    self.DHCP["netmask"],
                ),
                "ifconfig %s mtu 1400" % (self.SettingsEnable["AP_iface"]),
                "route add -net %s netmask %s gw %s"
                % (self.DHCP["subnet"], self.DHCP["netmask"], self.DHCP["router"]),
            ],
            "kill": [
                "iptables --flush",
                "iptables --table nat --flush",
                "iptables --delete-chain",
                "iptables --table nat --delete-chain",
                "ifconfig %s 0" % (self.SettingsEnable["AP_iface"]),
                "killall dhpcd 2>/dev/null",
            ],
            "hostapd": [
                "interface={}\n".format(str(self.Settings.WLANCard.currentText())),
                "ssid={}\n".format(str(self.EditApName.text())),
                "channel={}\n".format(str(self.EditChannel.value())),
                "bssid={}\n".format(str(self.EditBSSID.text())),
            ],
            "dhcp-server": [
                "authoritative;\n",
                "default-lease-time {};\n".format(self.DHCP["leasetimeDef"]),
                "max-lease-time {};\n".format(self.DHCP["leasetimeMax"]),
                "subnet %s netmask %s {\n"
                % (self.DHCP["subnet"], self.DHCP["netmask"]),
                "option routers {};\n".format(self.DHCP["router"]),
                "option subnet-mask {};\n".format(self.DHCP["netmask"]),
                "option broadcast-address {};\n".format(self.DHCP["broadcast"]),
                'option domain-name "%s";\n' % (str(self.EditApName.text())),
                "option domain-name-servers {};\n".format("8.8.8.8"),
                "range {};\n".format(self.DHCP["range"].replace("/", " ")),
                "}",
            ],
        }
        print("[*] Enable forwarding in iptables...")
        Refactor.set_ip_forward(1)
        # clean iptables settings
        for line in self.SettingsAP["kill"]:
            exec_bash(line)
        # set interface using ifconfig
        for line in self.SettingsAP["interface"]:
            exec_bash(line)
        # check if dhcp option is enabled.
        if self.FSettings.Settings.get_setting(
            "accesspoint", "dhcp_server", format=bool
        ):
            with open(C.DHCPCONF_PATH, "w") as dhcp:
                for line in self.SettingsAP["dhcp-server"]:
                    dhcp.write(line)
                dhcp.close()
                if not path.isdir("/etc/dhcp/"):
                    mkdir("/etc/dhcp")
                move(C.DHCPCONF_PATH, "/etc/dhcp/")
