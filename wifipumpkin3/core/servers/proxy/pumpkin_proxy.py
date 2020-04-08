from wifipumpkin3.core.config.globalimport import *
from collections import OrderedDict
from functools import partial
from threading import Thread
import queue
from scapy.all import *
import logging, os
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.servers.proxy.proxymode import *
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.widgets.docks.dock import DockableWidget

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    CONFIGINI_PATH = C.CONFIG_PP_INI
    _cmd_array = []
    ModSettings = True
    RunningPort = 8080
    ModType = "proxy" 
    TypePlugin =  1 

    def __init__(self,parent=None, **kwargs):
        super(PumpKinProxy,self).__init__(parent)
        self.setID(self.ID)
        self.parent = parent
        self.setTypePlugin(self.TypePlugin)
        self.setRunningPort(self.conf.get('proxy_plugins', 'pumpkinproxy_config_port'))

    @property
    def CMD_ARRAY(self):
        self.runDefaultRules()
        port_ssltrip = self.conf.get('proxy_plugins', 'pumpkinproxy_config_port')
        self._cmd_array=['-l', port_ssltrip]
        return self._cmd_array

    def boot(self):
        self.reactor= ProcessThread({'sslstrip3': self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

    @property
    def getPlugins(self):
        commands = self.config.get_all_childname('plugins')
        list_commands = []
        for command in commands:
            list_commands.append(self.ID + '.' + command)
        return list_commands

    def LogOutput(self,data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.logger.info(data)

    def parser_set_pumpkinproxy(self, status, plugin_name):
        try:
            # plugin_name = pumpkinproxy.no-cache 
            name_plugin,key_plugin = plugin_name.split('.')[0],plugin_name.split('.')[1]
            if key_plugin in self.config.get_all_childname('plugins'):
                self.config.set('plugins',key_plugin, status)
            else:
                print(display_messages('unknown plugin: {}'.format(key_plugin),error=True))
        except IndexError:
            print(display_messages('unknown sintax command',error=True))
