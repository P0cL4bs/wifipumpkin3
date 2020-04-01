from wifipumpkin3.core.packets.dhcpserver import DHCPThread
from wifipumpkin3.core.servers.dhcp.dhcp import DHCPServers


class PyDHCP(DHCPServers):
    Name = "Python DHCP Server"
    ID = "pydhcp_server"
    def __init__(self,parent=0):
        super(PyDHCP,self).__init__(parent)
        self._isRunning = False
        self._connected = {}

    def Initialize(self):
        self.ifaceHostapd = self.conf.get('accesspoint','interfaceAP')

    def setIsRunning(self,value):
        self._isRunning = value

    @property
    def getStatusReactor(self):
        return self._isRunning

    def get_DHCPoutPut(self, data):
        self._connected[data['MAC']] = data

    def boot(self):
        #if (not hasattr(self, 'reactor')):
        self.reactor = DHCPThread(self.ifaceHostapd,self.DHCPConf)
        self.reactor.DHCPProtocol._request.connect(self.get_DHCPoutPut)
        self.reactor.setObjectName(self.ID)
        #self.reactor.LoopDhcpStatus = True