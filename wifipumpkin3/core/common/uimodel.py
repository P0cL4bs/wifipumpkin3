from wifipumpkin3.core.config.globalimport import *
import weakref
import wifipumpkin3.core.utility.constants as C 
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.common.platforms import Linux

class CoreSettings(Linux):

    Name = "General"
    ID = "General"
    ConfigRoot = "General"
    Category="General"
    Icon=None
    __subitem=False
    conf={}


    def __init__(self,parent=0,FSettings=None):
        super(CoreSettings,self).__init__()
        self.parent  = parent
        self.conf    = SettingsINI(C.CONFIG_INI)

    def deleteObject(self,obj):
        ''' reclaim memory '''
        del obj

    @property
    def isSubitem(self):
        return self.__subitem

    def osWalkCallback(self,arg,directory,files):
        pass



class TabsWidget(Qt.QObject):
    Name="Generic"
    ID = "Generic"
    Icon = ""
    __subitem = False
    def __init__(self,parent=0,FSettings=None):
        super(TabsWidget,self).__init__()
        self.setObjectName(self.Name)
        #self.setTitle("{}".format(self.Name))
        self.conf = SuperSettings.getInstance()
        self.parent = parent

    @property
    def isSubitem(self):
        return self.__subitem



class PluginsUI(Qt.QObject):
    Name = "Default"
    Caption = "Default"
    ID = "Generic"
    def __init__(self,parent=0):
        super(PluginsUI,self).__init__(parent)
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self.sessionconfig ={}

    @property
    def config(self):
        return self.sessionconfigcd
        
    def deleteObject(self,obj):
        del obj
