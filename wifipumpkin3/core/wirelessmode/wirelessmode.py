from wifipumpkin3.core.config.globalimport import *
from re import *
from os import system, path, getcwd, popen, listdir, mkdir, chown
from shutil import move
from wifipumpkin3.core.widgets.default.session_config import *
from subprocess import check_output, Popen, PIPE, STDOUT, CalledProcessError, call
from wifipumpkin3.exceptions.errors.hostapdException import HostapdInitializeError
import sys
from wifipumpkin3.core.common.threads import WorkerProcess

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


class Mode(Qt.QObject):
    configApMode = "ap_mode"
    configRoot = "generic"
    SubConfig = "generic"
    ID = "GenericWirelessMode"
    Name = "Wireless Mode Generic"
    service = None
    reactor = None

    def __init__(self, parent=None, FSettings=None):
        super(Mode, self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self.SettingsAP = {}

        self.SessionConfig = SessionConfig.getInstance()
        self.interfacesLink = Refactor.get_interfaces()
        self.hostapd_path = self.getHostapdPath

    def checkifHostapdBinaryExist(self):
        """ check if hostapd binary file exist"""
        if path.isfile(self.hostapd_path):
            return True
        return False

    @property
    def getHostapdPath(self):
        return self.conf.get(self.configRoot, "{}_hostapd_path".format(self.configRoot))

    @property
    def getIptablesPath(self):
        return self.conf.get("iptables", "path_binary")

    def isChecked(self):
        return self.conf.get(self.configApMode, self.subConfig, format=bool)

    def get_soft_dependencies(self):
        """ check if Hostapd is installed """
        if not self.checkifHostapdBinaryExist():
            print(
                display_messages(
                    "{} is not installed in the system".format(
                        setcolor("hostapd", color="orange")
                    ),
                    error=True,
                )
            )
            sys.exit(1)

    def configure_network_AP(self):
        self.parent.configure_network_AP()

    @property
    def WirelessSettings(self):
        return self.SessionConfig.Wireless

    @property
    def Settings(self):
        pass

    def Initialize(self):
        pass

    def boot(self):
        pass

    def Shutdown(self):
        pass

    def addExtraHostapdSettings(self):
        time_seconds = self.conf.get("accesspoint", "ap_max_inactivity", format=int)
        settings = ["ap_max_inactivity={}\n".format(time_seconds)]
        for setting in settings:
            self.Settings.SettingsAP["hostapd"].append(setting)

    def Start(self):
        # check if soft deps is tnstalled
        self.get_soft_dependencies()
        self.Initialize()
        self.boot()
        self.PostStart()

    def PostStart(self):
        # set configure iptables
        self.setIptables()
        # set AP status true
        self.setStatusAP(True)

    def setStatusAP(self, value):
        self.conf.set("accesspoint", "status_ap", value)

    def setIptables(self):
        self.interfacesLink = Refactor.get_interfaces()
        print(display_messages("sharing internet connection with NAT...", info=True))
        self.ifaceHostapd = self.conf.get("accesspoint", "interface")
        self.threads_process = []
        for ech in self.conf.get_all_childname("iptables"):
            try:
                ech = self.conf.get("iptables", ech)
                if "$inet" in ech and self.interfacesLink["activated"][0] != None:
                    ech = ech.replace("$inet", self.interfacesLink["activated"][0])
                if "$wlan" in ech:
                    ech = ech.replace("$wlan", self.ifaceHostapd)

                if not "$inet" in ech:
                    cmd = {self.getIptablesPath: ech.split()}
                    self.threads_process.append(WorkerProcess(cmd))
            except Exception as e:
                print(e)

        for thread in self.threads_process:
            thread.start()
            thread.process.waitForFinished()
            del thread

    def Stop(self):
        self.Shutdown()

    def get_error_hostapdServices(self, data):
        """check error hostapd on mount AP """
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.Shutdown()
            raise HostapdInitializeError(
                "[ERROR] Hostpad Failed",
                "check output process hostapd.\n {}".format(data),
            )

    def check_Wireless_Security(self):
        """check if user add security password on AP"""
        self.confgSecurity = []
        wpa_type = self.conf.get("accesspoint", "wpa_type", format=int)
        wpa_algorithms = self.conf.get("accesspoint", "wpa_algorithms")
        wpa_sharedkey = self.conf.get("accesspoint", "wpa_sharedkey")

        if self.conf.get("accesspoint", "enable_security", format=bool):

            if 1 <= wpa_type <= 2:
                self.confgSecurity.append("wpa={}\n".format(wpa_type))
                self.confgSecurity.append("wpa_key_mgmt=WPA-PSK\n")
                self.confgSecurity.append("wpa_passphrase={}\n".format(wpa_sharedkey))
                self.confgSecurity.append("wpa_pairwise={}\n".format(wpa_algorithms))

            if wpa_type == 0:
                self.confgSecurity.append("auth_algs=1\n")
                self.confgSecurity.append("wep_default_key=0\n")
                if len(wpa_sharedkey) == 5 or len(wpa_sharedkey) == 13:
                    self.confgSecurity.append('wep_key0="{}"\n'.format(wpa_sharedkey))
                else:
                    self.confgSecurity.append("wep_key0={}\n".format(wpa_sharedkey))
            print(
                display_messages("enable security authentication wireless", info=True)
            )
            for config in self.confgSecurity:
                self.Settings.SettingsAP["hostapd"].append(config)

    def LogOutput(self, data):
        """ get inactivity client from hostapd response"""
        pass
