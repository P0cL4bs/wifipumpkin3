from core.config.globalimport import *
from core.common.uimodel import *
import weakref

class SessionConfig(TabsWidget):
    ConfigRoot="Settings"
    Name = "Settings"
    ID = "SessionConfig"
    Icon = "icons/settings-AP.png"
    __subitem = False
    tablayout={}
    tabwidget={}
    instances=[]
    def __init__(self,parent=None,FSettings=None):
        super(SessionConfig,self).__init__(parent,FSettings)
        self.__class__.instances.append(weakref.proxy(self))
        self.FSettings = SuperSettings.getInstance()
        self.title = self.__class__.__name__

        settingsItem = [setitem(self.parent ) for setitem in CoreSettings.__subclasses__()]
        self.settingsItem = {}

        for mod in settingsItem:
            self.settingsItem[mod.title]=mod
            #self.mainlayout.addWidget(mod)
            #Hack to add all the modules into class
            setattr(self.__class__,mod.ID,mod)

    @property
    def isSubitem(self):
        return self.__subitem

    @classmethod
    def getInstance(cls):
        return cls.instances[0]


