from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.servers.mitm import *
from wifipumpkin3.core.common.uimodel import *
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


class MitmController(PluginsUI, ControllerBlueprint):
    Name = "MITM"
    ID = "mitm_controller"
    Caption = "Activity Monitor"
    mitmhandler = {}
    SetNoMitmMode = QtCore.pyqtSignal(object)
    mitm_infor = {}

    @staticmethod
    def getID():
        return MitmController.ID

    def __init__(self, parent=None, **kwargs):
        super(MitmController, self).__init__(parent)
        self.parent = parent
        # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        self.conf = SuperSettings.getInstance()

        # find all mitm plugin files
        __manipulator = [
            prox(parent=self.parent) for prox in mitmmode.MitmMode.__subclasses__()
        ]
        # Keep Proxy in a dictionary
        for k in __manipulator:
            # print(k.Name, 'mitmcontroller')
            self.mitmhandler[k.Name] = k
            self.mitm_infor[k.ID] = {
                "ID": k.ID,
                "Name": k.Name,
                "Activate": k.isChecked(),
                "Author": k.Author,
                "Logger": k.LogFile,
                "ConfigPath": k.CONFIGINI_PATH,
                "Description": k.Description,
                "Config": k.getConfig,
                "TypeButton": k.TypeButton,
            }

        # set all mitm plugin as child class
        for n, p in self.mitmhandler.items():
            setattr(self, p.ID, p)

    @property
    def ActiveDock(self):
        manobj = []
        for manip in self.Active:
            manobj.append(manip.dockwidget)
        return manobj

    @property
    def Active(self):
        manobj = []
        for manip in self.mitmhandler.values():
            if manip.isChecked():
                manobj.append(manip)
        return manobj

    @property
    def ActiveReactor(self):
        reactor = []
        for i in self.Active:
            reactor.append(i.reactor)
        return reactor

    @property
    def get(self):
        return self.mitmhandler

    def getInfo(self, excluded=()):
        if not excluded:
            return self.mitm_infor
        result = {}
        for item in self.mitm_infor:
            result[item] = {}
            for subItem in self.mitm_infor[item]:
                if not subItem in excluded:
                    result[item][subItem] = self.mitm_infor[item][subItem]
        return result

    @classmethod
    def disable(cls, val=True):
        pass

    @property
    def disableproxy(self, name):
        pass

    def Start(self):
        for i in self.Active:
            i.boot()

    @property
    def getAllReactor(self):
        reactor = []
        for i in self.Active:
            reactor.append(i.reactor)
        return reactor

    def getReactorInfo(self):
        info_reactor = {}
        for reactor in self.getAllReactor:
            info_reactor[reactor.getID()] = {
                "ID": reactor.getID(),
                "PID": reactor.getpid(),
            }
        return info_reactor

    def Stop(self):
        for i in self.Active:
            i.shutdown()
