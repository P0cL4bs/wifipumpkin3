from core.config.globalimport import *
from core.common.uimodel import *


from core.widgets.default import *

class DefaultWidget(Qt.QObject):
    def __init__(self,parent = None,**kwargs):
        super(DefaultWidget,self).__init__()
        self.parent = parent
        self.FSettings = SuperSettings.getInstance()
        self.defaultui = []
        self.allui =[]
        self.__tabbyname = {}
        __defaultui = [ui(parent,self.FSettings) for ui in TabsWidget.__subclasses__()]
        for ui in __defaultui:
            if not  ui.isSubitem:
                self.defaultui.append(ui)
            self.allui.append(ui)
            self.__tabbyname[ui.Name]=ui
            setattr(self.__class__,ui.ID,ui)

    def CoreTabsByName(self,name):

        if self.__tabbyname.has_key(name):
            return self.__tabbyname[name]

    @property
    def CoreTabs(self):
        return self.defaultui

