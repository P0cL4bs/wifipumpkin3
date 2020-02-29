from core.config.globalimport import *
from collections import OrderedDict
from functools import partial
from threading import Thread
import queue
from scapy.all import *
import logging
#from plugins.analyzers import *

import core.utility.constants as C
from core.common.platforms import setup_logger
from core.servers.proxy.proxymode import *
from core.utility.collection import SettingsINI
# from core.widgets.docks.dockmonitor import (
#     dockTCPproxy,dockUrlMonitor
# )
from core.common.uimodel import *
from plugins.analyzers import *
from core.widgets.docks.dock import DockableWidget

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
    Name = "pumpkinproxy_plugin"
    Author = "Pumpkin-Dev"
    ID = "pumpkinproxy"
    Description = "Sniff for intercept network traffic on UDP,TCP protocol get password,hash,image,etc..."
    Hidden = False
    LogFile = C.LOG_PUMPKINPROXY
    _cmd_array = ['-m' ,'proxy' ,'--hostname',
     '0.0.0.0', '--port' ,'8080','--plugins','plugins.plugins.RedirectToCustomServerPlugin']
    ModSettings = True
    ModType = "proxy" 
    TypePlugin =  1 

    def __init__(self,parent=None, **kwargs):
        super(PumpKinProxy,self).__init__(parent)
        self.setID(self.Name)
        self.setTypePlugin(self.TypePlugin)
        self.config = SettingsINI(C.CONFIG_TP_INI)
        self.plugins = []
        self.parent = parent
        self.bt_SettingsDict = {}
        self.check_PluginDict = {}

    def setPluginOption(self, name, status):
        ''' get each plugins status'''
        # enable realtime disable and enable plugin
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.reactor.disablePlugin(name, status)
        self.conf.set('plugins', name, status)

    def search_all_ProxyPlugins(self):
        ''' load all plugins function '''
        plugin_classes = default.PSniffer.__subclasses__()
        for p in plugin_classes:
            if p().Name != 'httpCap':
                self.plugins.append(p())

    # def boot(self):
    #     #self.handler = self.parent.Plugins.MITM
    #     iface =  self.conf.get('accesspoint','interfaceAP')
    #     self.reactor= TCPProxyCore(iface, self.parent.currentSessionID)
    #     self.reactor.setObjectName(self.Name)
    #     self.reactor._ProcssOutput.connect(self.LogOutput)

    def LogOutput(self,data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.logger.info(data)