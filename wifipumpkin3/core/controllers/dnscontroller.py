from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.servers.dns import *


class DNSController(ControllerBlueprint):
    
    ID = 'dns_controller'

    @staticmethod
    def getID():
        return DNSController.ID

    def __init__(self,parent=None,**kwargs):
        super(DNSController,self).__init__()
        self.parent = parent
         # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        self.DNSSettings = DNSBase.DNSSettings.getInstance()
        for dns in self.DNSSettings.dnslist:
            setattr(self,dns.ID,dns)

    def Start(self):
        self.Active.Start()

    @property
    def ActiveReactor(self):
        return self.Active.reactor

    @property
    def Active(self):
        for dns in self.DNSSettings.dnslist:
            if dns.isChecked():
                return dns

    def getReactorInfo(self):
        info_reactor = {}
        info_reactor[self.ActiveReactor.getID()] = {
            'ID' : self.ActiveReactor.getID(), 'PID' : self.ActiveReactor.getpid()
            }
        return info_reactor