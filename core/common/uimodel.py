from core.config.globalimport import *
import weakref
import core.utility.constants as C 
from core.utility.collection import SettingsINI
from core.common.platforms import Linux

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
        self.FSettings = SuperSettings.getInstance()
        self.parent = parent

    @property
    def isSubitem(self):
        return self.__subitem