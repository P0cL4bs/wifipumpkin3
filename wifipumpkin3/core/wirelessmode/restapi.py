from wifipumpkin3.core.config.globalimport import *
import weakref
from os import path, popen, mkdir
from subprocess import check_output, STDOUT, CalledProcessError
from wifipumpkin3.core.common.threads import ProcessHostapd
from wifipumpkin3.core.wirelessmode.wirelessmode import Mode
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.printer import display_messages, setcolor
from wifipumpkin3.exceptions.errors.networkException import *
from wifipumpkin3.exceptions.errors.hostapdException import *
import configparser

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


class RestAPI(Mode):
    configRoot = "restapi"
    subConfig = "restapi"
    ID = "restapi"
    Name = "Wireless API AP Mode"

    def __init__(self, parent=0):
        super(RestAPI, self).__init__(parent)
        self.parent = parent
        self.confgSecurity = []

    @property
    def Settings(self):
        return RestApiSettings.getInstance()

    def getSettings(self):
        return self.Settings

    def Initialize(self):
        self.Settings.Configure()
        self.Settings.checkNetworkAP

        self.check_Wireless_Security()
        # add extra hostapd settings
        self.addExtraHostapdSettings()

        ignore = ("interface=", "ssid=", "channel=", "essid=")
        with open(C.HOSTAPDCONF_PATH, "w") as apconf:
            for i in self.Settings.SettingsAP["hostapd"]:
                apconf.write(i)
            apconf.close()

    def boot(self):
        # create thread for hostapd and connect get_Hostapd_Response functio
        self.reactor = ProcessHostapd(
            {self.getHostapdPath: [C.HOSTAPDCONF_PATH]}, "MDSNjD"
        )
        self.reactor.setObjectName("hostapd_{}".format(self.ID))
        self.reactor.statusAP_connected.connect(self.get_Hostapd_Response)
        self.reactor.statusAPError.connect(self.get_error_hostapdServices)

    def get_Hostapd_Response(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            print(
                display_messages(
                    "{} client has left AP ".format(setcolor(data, color="red")),
                    info=True,
                )
            )

    def get_error_hostapdServices(self, data):
        """check error hostapd on mount AP """
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.Shutdown()
            print(
                HostapdInitializeError(
                    "[ERROR] Hostpad Failed",
                    "check output process hostapd.\n {}".format(data),
                )
            )

    def setNetworkManager(self, interface=str, Remove=False):
        """ mac address of interface to exclude """
        networkmanager = C.NETWORKMANAGER
        config = configparser.RawConfigParser()
        MAC = Linux.get_interface_mac(interface)
        exclude = {
            "MAC": "mac:{}".format(MAC),
            "interface": "interface-name:{}".format(interface),
        }
        if not Remove:
            if path.exists(networkmanager):
                config.read(networkmanager)
                try:
                    config.add_section("keyfile")
                except configparser.DuplicateSectionError:
                    config.set(
                        "keyfile",
                        "unmanaged-devices",
                        "{}".format(
                            exclude["interface"] if MAC != None else exclude["MAC"]
                        ),
                    )
                else:
                    config.set(
                        "keyfile",
                        "unmanaged-devices",
                        "{}".format(
                            exclude["interface"] if MAC != None else exclude["MAC"]
                        ),
                    )
                finally:
                    with open(networkmanager, "wb") as configfile:
                        config.write(configfile)
                return True
            return False
        elif Remove:
            if path.exists(networkmanager):
                config.read(networkmanager)
                try:
                    config.remove_option("keyfile", "unmanaged-devices")
                    with open(networkmanager, "wb") as configfile:
                        config.write(configfile)
                        return True
                except configparser.NoSectionError:
                    return True
            return False


class RestApiSettings(CoreSettings):
    Name = "RestApi"
    ID = "RestAPI"
    Category = "Wireless"
    instances = []

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    def __init__(self, parent):
        super(RestApiSettings, self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))
        self.conf = SettingsINI.getInstance()

        self.title = self.__class__.__name__
        self.SettingsAP = {}

        self.interfaces = Linux.get_interfaces()
        self.DHCP = self.getDHCPConfig()

    def getDHCPConfig(self):
        DHCP = {}
        DHCP["leasetimeDef"] = self.conf.get("dhcp", "leasetimeDef")
        DHCP["leasetimeMax"] = self.conf.get("dhcp", "leasetimeMax")
        DHCP["subnet"] = self.conf.get("dhcp", "subnet")
        DHCP["router"] = self.conf.get("dhcp", "router")
        DHCP["netmask"] = self.conf.get("dhcp", "netmask")
        DHCP["broadcast"] = self.conf.get("dhcp", "broadcast")
        DHCP["range"] = self.conf.get("dhcp", "range")
        return DHCP

    def Configure(self):
        """ configure interface and dhcpd for mount Access Point """
        self.ifaceHostapd = self.conf.get("accesspoint", "interface")
        self.SettingsAP = {
            "interface": [
                "ifconfig %s up" % (self.ifaceHostapd),
                "ifconfig %s %s netmask %s"
                % (self.ifaceHostapd, self.DHCP["router"], self.DHCP["netmask"]),
                "ifconfig %s mtu 1400" % (self.ifaceHostapd),
                "route add -net %s netmask %s gw %s"
                % (self.DHCP["subnet"], self.DHCP["netmask"], self.DHCP["router"]),
            ],
            "kill": [
                "iptables -w --flush",
                "iptables -w --table nat --flush",
                "iptables -w --delete-chain",
                "iptables -w --table nat --delete-chain",
                "killall dhpcd 2>/dev/null",
                "ifconfig {} down".format(self.ifaceHostapd),
                "ifconfig {} up".format(self.ifaceHostapd),
                "ifconfig {} 0".format(self.ifaceHostapd),
            ],
            "hostapd": [
                "interface={}\n".format(self.ifaceHostapd),
                "ssid={}\n".format(self.conf.get("accesspoint", "ssid")),
                "channel={}\n".format(self.conf.get("accesspoint", "channel")),
                "bssid={}\n".format(self.conf.get("accesspoint", "bssid")),
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
                'option domain-name "%s";\n' % (self.conf.get("accesspoint", "ssid")),
                "option domain-name-servers {};\n".format("8.8.8.8"),
                "range {};\n".format(self.DHCP["range"].replace("/", " ")),
                "}",
            ],
        }
        print(display_messages("enable forwarding in iptables...", sucess=True))
        Linux.set_ip_forward(1)
        # clean iptables settings
        for line in self.SettingsAP["kill"]:
            exec_bash(line)
        # set interface using ifconfig
        for line in self.SettingsAP["interface"]:
            exec_bash(line)
        # check if dhcp option is enabled.
        if self.conf.get("accesspoint", "dhcp_server", format=bool):
            with open(C.DHCPCONF_PATH, "w") as dhcp:
                for line in self.SettingsAP["dhcp-server"]:
                    dhcp.write(line)
                dhcp.close()
                if not path.isdir("/etc/dhcp/"):
                    mkdir("/etc/dhcp")
                move(C.DHCPCONF_PATH, "/etc/dhcp/")

    def checkNetworkAP(self):
        "this will be checked on web interface "
        return True

    def get_supported_interface(self, dev):
        """ get all support mode from interface wireless  """
        _iface = {"info": {}, "Supported": []}
        try:
            output = check_output(
                ["iw", dev, "info"], stderr=STDOUT, universal_newlines=True
            )
            for line in output.split("\n\t"):
                _iface["info"][line.split()[0]] = line.split()[1]
            rulesfilter = '| grep "Supported interface modes" -A 10 | grep "*"'
            supportMode = popen(
                "iw phy{} info {}".format(_iface["info"]["wiphy"], rulesfilter)
            ).read()
            for mode in supportMode.split("\n\t\t"):
                _iface["Supported"].append(mode.split("* ")[1])
        except CalledProcessError:
            return _iface
        return _iface
