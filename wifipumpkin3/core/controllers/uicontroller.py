from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.servers.dhcp import *
from wifipumpkin3.core.ui import *

class UIController(ControllerBlueprint):
    ui_handler = {}
    def __init__(self,parent):
        super(UIController,self).__init__()
        self.parent = parent
        __manipulator= [prox(parent=self.parent) for prox in uimode.WidgetBase.__subclasses__()]
        
        for k in __manipulator:
            self.ui_handler[k.Name]=k

        for n,p in self.ui_handler.items():
            setattr(self,p.ID,p)