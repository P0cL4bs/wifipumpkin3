import socket
import core.utility.constants as C
from core.utility.printer import display_messages,colors
from PyQt4.QtCore import pyqtSignal,QObject
from mitmproxy import proxy, flow, options
from mitmproxy.proxy.server import ProxyServer
from core.utility.collection import SettingsINI
from core.servers.proxy.http.controller.handler import MasterHandler
from core.servers.proxy.tcp.intercept import TH_SniffingPackets


class PumpkinProxy(QObject):
    '''Thread: run Pumpkin-Proxy mitmproxy on brackground'''
    send = []
    def __init__(self,session=None):
        QObject.__init__(self)
        self.session = session

    def start(self):
        print(display_messages('proxy running on port:8080',sucess=True))
        opts = options.Options(listen_port=8080,mode="transparent")
        config = proxy.ProxyConfig(opts)
        self.server = ProxyServer(config)
        self.server.allow_reuse_address = True
        self.m = MasterHandler(opts,self.server,self.session)
        self.m.run(self.send)

    def stop(self):
        self.server.socket.close()
        self.server.shutdown()
        self.m.shutdown()
        print(display_messages(' {} successfully stopped.'.format(self.objectName()),info=True))



class SniffingPackets(QObject):
    def __init__(self, main):
        QObject.__init__(self)
        self.list_sniffing  = {'Thread':[]}
        self.main           = main
        self.conf           = SettingsINI(C.CONFIG_INI)
        self.interface      = self.conf.get('accesspoint','interfaceAP')

    def setup(self):

        #create thread for plugin Pumpkin-Proxy
        self.Thread_PumpkinProxy = PumpkinProxy('')
        #self.Thread_PumpkinProxy.send.connect(self.get_PumpkinProxy_output)
        self.Thread_PumpkinProxy.setObjectName('pumpkin-proxy')
        self.list_sniffing['Thread'].append(self.Thread_PumpkinProxy)

        self.tcp_proxy = TH_SniffingPackets(self.interface, '')
        self.tcp_proxy.setObjectName('tcp-proxy')
        self.list_sniffing['Thread'].append(self.tcp_proxy)

    def get_PumpkinProxy_output(self, data):
        self.main.ui_monitor.append_parserData3(data)

    def get_output(self,data):
        print(data)

    def start(self):
        self.setup()
        for thread in self.list_sniffing['Thread']:
            thread.start()

    def stop(self):
        for thread in self.list_sniffing['Thread']:
            thread.stop()