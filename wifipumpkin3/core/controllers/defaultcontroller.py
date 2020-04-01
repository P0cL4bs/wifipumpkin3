import weakref
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.widgets.default import *

from wifipumpkin3.core.controllers.wirelessmodecontroller import *
from wifipumpkin3.core.controllers.dhcpcontroller import *
from wifipumpkin3.core.controllers.proxycontroller import *
from wifipumpkin3.core.controllers.mitmcontroller import *
from wifipumpkin3.core.controllers.dnscontroller import *
from wifipumpkin3.core.controllers.uicontroller import *

class DefaultController(Qt.QObject):

    _controllers = {}
    instances=[]

    def __init__(self,parent = None,**kwargs):
        super(DefaultController,self).__init__()
        self.__class__.instances.append(weakref.proxy(self))
        self.parent = parent
        self.FSettings = SuperSettings.getInstance()
        self.defaultui = []
        self.allui =[]
        self.__tabbyname = {}
        # load all pluginsUI class 
        __defaultui = [ui(parent,self.FSettings) for ui in TabsWidget.__subclasses__()]
        for ui in __defaultui:
            if not  ui.isSubitem:
                self.defaultui.append(ui)
            self.allui.append(ui)
            self.__tabbyname[ui.Name]=ui
            setattr(self.__class__,ui.ID,ui)
        
        self.intialize_controllers(self.parent)

    def intialize_controllers(self, parent):
        """ initialize all controllers"""
        WirelessModeController(parent)
        DHCPController(parent)
        DNSController(parent)
        UIController(parent)

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    def addController(self, instance):
        """ add controller instance app """
        self._controllers[instance.getID()] = instance 

    def getController(self, name):
        """ get controller instance app """
        if name:
            return self._controllers.get(name)
        return self._controllers

    def CoreTabsByName(self,name):

        if self.__tabbyname.has_key(name):
            return self.__tabbyname[name]

    @property
    def CoreTabs(self):
        return self.defaultui

