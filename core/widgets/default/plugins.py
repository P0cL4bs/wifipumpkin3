from core.common.uimodel import *
from PyQt5.QtCore import pyqtSignal



class Plugins(TabsWidget):
    Name = "Plugins"
    ID = "Plugins"
    __subitem = False
    sendSingal_disable = pyqtSignal(object)
    def __init__(self,parent,FSettings=None):
        super(Plugins,self).__init__(parent,FSettings)
        self.__plugins = [plug(parent) for plug in PluginsUI.__subclasses__()]
        print(self.__plugins)
        for wid in self.__plugins:
            setattr(self,wid.Name,wid)


