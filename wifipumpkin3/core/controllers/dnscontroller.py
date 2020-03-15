from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.servers.dns import *


class DNSController(ControllerBlueprint):
    

    def __init__(self,parent=None,**kwargs):
        super(DNSController,self).__init__()
        self.parent = parent
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
