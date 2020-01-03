from core.config.globalimport import *
from core.packets.dhcpserver import DHCPThread
from core.servers.dhcp.dhcp import DHCPServers

class PyDHCP(DHCPServers):
    Name = "Python DHCP Server"
    ID = "pydhcp_server"
    def __init__(self,parent=0):
        super(PyDHCP,self).__init__(parent)
        self._isRunning = False
    def Initialize(self):
        self.ifaceHostapd = self.conf.get('accesspoint','interfaceAP')

    def setIsRunning(self,value):
        self._isRunning = value

    @property
    def getStatusReactor(self):
        return self._isRunning

    def get_DHCPoutPut(self, data):
        print(data)

    def boot(self):
        #if (not hasattr(self, 'reactor')):
        threadDHCP = DHCPThread(self.ifaceHostapd,self.DHCPConf)
        threadDHCP.DHCPProtocol._request.connect(self.get_DHCPoutPut)
        self.reactor = threadDHCP
        #self.reactor.LoopDhcpStatus = True