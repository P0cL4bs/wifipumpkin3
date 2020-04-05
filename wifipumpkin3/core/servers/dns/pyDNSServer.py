from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.servers.dns.DNSBase import DNSBase
from wifipumpkin3.core.packets.dnsserver import  DNSServerThread

class PyDNSServer(DNSBase):
    ID = "pydns_server"
    Name = "PyDNS Server"
    Author = 'Samuel Colvin @samuelcolvin'
    LogFile = C.LOG_PYDNSSERVER
    ExecutableFile = ""

    def __init__(self,parent):
        super(PyDNSServer,self).__init__(parent)
        #self.logger.setIgnore(True)

    @property
    def commandargs(self):
        pass

    def LogOutput(self, data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.logger.info(data)

    def boot(self):
        #TODO : the pyDnsServer is disabled because problem dns instance setting os
        # future: check another alternative
        self.reactor = DNSServerThread(self.conf)
        self.reactor.sendRequests.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)  # use dns2proxy as DNS server
