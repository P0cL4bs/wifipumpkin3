from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.servers.proxy import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
import copy
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


class ProxyModeController(PluginsUI, ControllerBlueprint):
    Name = "Proxy"
    Caption = "Enable Proxy Server"
    ID = "proxy_controller"
    proxies = {}
    proxies_infor = {}
    SetNoProxy = QtCore.pyqtSignal(object)
    dockMount = QtCore.pyqtSignal(bool)

    @staticmethod
    def getID():
        return ProxyModeController.ID

    def __init__(self, parent=None, **kwargs):
        super(ProxyModeController, self).__init__(parent)
        self.parent = parent
        # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        self.conf = SuperSettings.getInstance()

        # load all plugin proxy
        __proxlist = [
            prox(parent=self.parent) for prox in proxymode.ProxyMode.__subclasses__()
        ]

        # Keep Proxy in a dictionary
        for k in __proxlist:
            self.proxies[k.Name] = k

            self.proxies_infor[k.ID] = {
                "ID": k.ID,
                "Name": k.Name,
                "Port": k.getRunningPort(),
                "Activate": k.isChecked(),
                "Author": k.Author,
                "Logger": k.LogFile,
                "ConfigPath": k.CONFIGINI_PATH,
                "Description": k.Description,
                "Config": k.getConfig,
                "TypeButton": k.TypeButton,
            }

        # set all proxy plugin as child class
        for n, p in self.proxies.items():
            if hasattr(p, "ID"):
                setattr(self, p.ID, p)

    def isChecked(self):
        return self.conf.get("plugins", self.ID, format=bool)

    @property
    def ActiveDocks(self):
        return self.Active.dockwidget

    @property
    def ActiveReactor(self):
        reactor = []
        for act in self.proxies.values():
            if act.isChecked():
                if act.Name == "noproxy":
                    reactor.append(act.reactor)
                    reactor.append(act.subreactor)
                else:
                    reactor.append(act.reactor)
                    if act.subreactor:
                        reactor.append(act.subreactor)
        return reactor

    @property
    def Active(self):
        for act in self.proxies.values():
            # exclude tcp proxy log
            if act.getTypePlugin() != 2:
                # print(act.isChecked(),act.Name)
                if act.isChecked():
                    return act

    @property
    def ActiveLoad(self):
        """ load all proxies type checkbox UI in tab plugins """
        proxies = []
        for act in self.proxies.values():
            if act.isChecked():
                proxies.append(act)
        return proxies

    @property
    def get(self):
        return self.proxies

    def getInfo(self, excluded=()):
        if not excluded:
            return self.proxies_infor
        result = {}
        for item in self.proxies_infor:
            result[item] = {}
            for subItem in self.proxies_infor[item]:
                if not subItem in excluded:
                    result[item][subItem] = self.proxies_infor[item][subItem]
        return result
        

    @classmethod
    def disable(cls, val=True):
        pass

    @property
    def disableproxy(self, name):
        pass

    def Start(self):
        self.Active.Initialize()
        self.Active.Serve()
        self.Active.boot()
        # load proxy checkbox all type all proxies
        for proxy in self.ActiveLoad:
            if proxy.Name != self.Active.Name:
                proxy.Initialize()
                proxy.Serve()
                proxy.boot()

    @property
    def getReactor(self):
        return self.Active.reactor

    def getReactorInfo(self):
        info_reactor = {}
        try:
            info_reactor[self.getReactor.getID()] = {
                "ID": self.getReactor.getID(),
                "PID": self.getReactor.getpid(),
            }
        except AttributeError:
            pass
        return info_reactor

    def Stop(self):
        self.Active.Serve(False)
        self.Active.shutdown()

    def SaveLog(self):
        self.Active.SaveLog()
