from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.servers.dhcp import *

class DHCPController(ControllerBlueprint):
    def __init__(self,parent):
        super(DHCPController,self).__init__()
        self.parent = parent
        __dhcpmode = dhcp.DHCPSettings.instances[0].dhmode
        self.mode = {}
        for k in __dhcpmode:
            self.mode[k.ID]=k
            
    def Start(self):
        self.Active.Start()

    @property
    def ActiveService(self):
        return self.Active.service

    @property
    def Active(self):
        for i in self.mode.values():
            if i.isChecked():
                return i
    @property
    def ActiveReactor(self):
        #reactor=[self.Active.reactor,self.Active.service]
        return self.Active.reactor

    def Stop(self):
        self.Active.Stop()

    def getReactorInfo(self):
        info_reactor = {}
        info_reactor[self.ActiveReactor.getID()] = {
            'ID' : self.ActiveReactor.getID(), 'PID' : self.ActiveReactor.getpid()
            }
        return info_reactor

