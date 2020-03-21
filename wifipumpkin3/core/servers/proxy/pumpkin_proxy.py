from wifipumpkin3.core.config.globalimport import *
from collections import OrderedDict
from functools import partial
from threading import Thread
import queue
from scapy.all import *
import logging, os
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.common.platforms import setup_logger
from wifipumpkin3.core.servers.proxy.proxymode import *
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.widgets.docks.dock import DockableWidget

class TCPProxyDock(DockableWidget):
    id = "TCPProxy"
    title = "TCPProxy"

    def __init__(self,parent=0,title="",info={}):
        super(TCPProxyDock,self).__init__(parent,title,info={})
        self.setObjectName(self.title)
        self.THeaders  = OrderedDict([ ('Plugin',[]),('Logging',[])])


    def writeModeData(self,data):
        ''' get data output and add on QtableWidgets '''
        self.THeaders['Plugin'].append(data.keys()[0])
        self.THeaders['Logging'].append(data[data.keys()[0]])
        Headers = []
        print(data)

    def stopProcess(self):
        pass

class PumpKinProxy(ProxyMode):
    Name = "PumpkinProxy 3"
    Author = "Pumpkin-Dev"
    ID = "pumpkinproxy"
    Description = "Sniff for intercept network traffic on UDP,TCP protocol get password,hash,image,etc..."
    Hidden = False
    LogFile = C.LOG_PUMPKINPROXY
    _cmd_array = []
    ModSettings = True
    RunningPort = 8080
    ModType = "proxy" 
    TypePlugin =  1 

    def __init__(self,parent=None, **kwargs):
        super(PumpKinProxy,self).__init__(parent)
        self.setID(self.ID)
        self.setTypePlugin(self.TypePlugin)
        self.setRunningPort(self.conf.get('proxy_plugins', 'pumpkinproxy_config_port'))
        self.config = SettingsINI(C.CONFIG_TP_INI)

    @property
    def CMD_ARRAY(self):
        self.runDefaultRules()
        port_ssltrip = self.conf.get('proxy_plugins', 'pumpkinproxy_config_port')
        self._cmd_array=['-l', port_ssltrip]
        return self._cmd_array

    def boot(self):
        self.reactor= ProcessThread({'sslstrip3': self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.Name)
        
    def LogOutput(self,data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.logger.info(data)