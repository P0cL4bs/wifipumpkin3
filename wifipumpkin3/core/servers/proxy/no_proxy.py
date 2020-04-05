from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.servers.proxy.proxymode import ProxyMode

class NoProxy(ProxyMode):
    Name="noproxy"
    ID="noproxy"
    Description = "Runnning without proxy redirect traffic"
    Author = "Pumpkin-Dev"
    Hidden = True
    TypePlugin = 1

    def __init__(self, parent, **kwargs):
        super(NoProxy, self).__init__(parent)
        self.setID(self.ID)
        self.setTypePlugin(self.TypePlugin)
        
    def boot(self):
        pass