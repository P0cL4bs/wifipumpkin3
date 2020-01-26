from core.common.accesspoint import AccessPoint
#from core.common.sniffing import SniffingPackets
from core.common.terminal import ConsoleUI
from core.widgets.window import ui_TableMonitorClient,ui_MonitorSniffer
from core.utility.collection import SettingsINI
import core.utility.constants  as C
from core.utility.printer import display_messages,setcolor
from termcolor import colored
import npyscreen, threading

from core.common.defaultwidget import *
from core.config.globalimport import *

from core.controllers.wirelessmodecontroller import *
from core.controllers.dhcpcontroller import *
from core.servers.dhcp.dhcp import *
from core.controllers.proxycontroller import *
from core.controllers.mitmcontroller import *
from core.controllers.dnscontroller import *


approot = QtCore.QCoreApplication.instance()

class TestApp(npyscreen.NPSApp):
    def main(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F  = npyscreen.Form(name = "Welcome to Npyscreen",)
        t  = F.add(npyscreen.TitleText, name = "Text:",)
        fn = F.add(npyscreen.TitleFilename, name = "Filename:")
        fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
        dt = F.add(npyscreen.TitleDateCombo, name = "Date:")
        s  = F.add(npyscreen.TitleSlider, out_of=12, name = "Slider")
        ml = F.add(npyscreen.MultiLineEdit,
               value = """try typing here!\nMutiline text, press ^R to reformat.\n""",
               max_height=5, rely=9)
        ms = F.add(npyscreen.TitleSelectOne, max_height=4, value = [1,], name="Pick One",
                values = ["Option1","Option2","Option3"], scroll_exit=True)
        ms2= F.add(npyscreen.TitleMultiSelect, max_height =-2, value = [1,], name="Pick Several",
                values = ["Option1","Option2","Option3"], scroll_exit=True)

        # This lets the user interact with the Form.
        F.edit()

        print(ms.get_selected_objects())

class PumpkinShell(Qt.QObject, ConsoleUI):
    """
    :parameters
        options : parse_args
    """
    instances=[]

    def __init__(self,options):
        ConsoleUI.__init__(self)
        super(PumpkinShell, self).__init__()
        self.__class__.instances.append(weakref.proxy(self))
        self.options    = options
        #self.sniffs     = SniffingPackets(self)
        self.conf       = SettingsINI(C.CONFIG_INI)
        self.conf_pproxy    = SettingsINI(C.CONFIG_PP_INI)
        self.conf_tproxy    = SettingsINI(C.CONFIG_TP_INI)
        self.ac         = AccessPoint(self)

        self.currentSessionID = 'teste'


        self.coreui = DefaultWidget(self)
        self.wireless = WirelessModeController(self)
        self.dhcpcontrol = DHCPController(self)
        self.dnsserver = DNSController(self)
        self.logger_manager = LoggerManager.getInstance()

        self.proxy = self.coreui.Plugins.Proxy
        self.mitmhandler = self.coreui.Plugins.MITM

        self.ac.sendStatusPoint.connect(self.getAccessPointStatus)
        self.ui_table   = ui_TableMonitorClient(self)
        self.ui_monitor = ui_MonitorSniffer(self)
        self.commands = {'interface': 'interfaceAP','ssid': 'ssid',
        'bssid': 'bssid','channel':'channel'}
        self.Apthreads = {'RogueAP': []}
        self.setOptions()

    def setOptions(self):
        if (self.options.pulp):
            self.loadPulpFiles(self.options.pulp)
        elif (self.options.xpulp):
            self.onecmd(self.options.xpulp, ";")

    def loadPulpFiles(self, file, data=None):
        ''' load and execute all commands in file pulp separate for \n '''
        if os.path.isfile(file):
            with open(self.options.pulp, 'r') as f:
                data = f.read()
                f.close()
            if (data != None):
                self.onecmd(data, separator='\n')
        
    def getAccessPointStatus(self,status):
        self.ui_table.startThreads()
        self.ui_monitor.startThreads()


    def do_start(self,args):
        ''' start access point '''
        # if (not self.countThreads() > 0): 
        #     self.sniffs.start()
        #     self.ac.start()
        #     self.addThreads(self.sniffs)
        #     return self.addThreads(self.ac)
        # print(display_messages('the access point is running. [{}]'.format(
        #     self.conf.get('accesspoint','ssid')
        # ),error=True))
        self.interfaces = Linux.get_interfaces()
        if (not self.conf.get("accesspoint", self.commands['interface']) in self.interfaces):
            print(display_messages('The interface not found! ',error=True))
            sys.exit(1)

        self.conf.set('accesspoint',self.commands['interface'],self.options.interface)
        self.conf.set('accesspoint','current_session',self.options.session)

        if self.wireless.Start() != None: return
        self.dhcpcontrol.Start()
        self.dnsserver.Start()
        self.proxy.Start()
        self.mitmhandler.Start()

        self.Apthreads['RogueAP'].insert(0,self.wireless.ActiveReactor)
        self.Apthreads['RogueAP'].insert(1,self.dhcpcontrol.ActiveReactor)
        self.Apthreads['RogueAP'].insert(2,self.dnsserver.ActiveReactor)
        self.Apthreads['RogueAP'].extend(self.proxy.ActiveReactor)
        self.Apthreads['RogueAP'].extend(self.mitmhandler.ActiveReactor)


        print(display_messages('sharing internet connection with NAT...', info=True))
        self.ifaceHostapd = self.conf.get('accesspoint','interfaceAP')
        try:
            for ech in self.conf.get_all_childname('iptables'):
                ech = self.conf.get('iptables', ech)
                if '$inet' in ech:
                    ech = ech.replace('$inet',self.interfaces['activated'][0])
                if '$wlan' in ech:
                    ech = ech.replace('$wlan',self.ifaceHostapd)
                popen(ech)
        except Exception as e:
            print(e)

        
        for thread in self.Apthreads['RogueAP']:
            if thread is not None:
                QtCore.QThread.sleep(1)
                if not (isinstance(thread, list)):  
                    thread.start()

        #self.dns = DNSServer(self.ifaceHostapd, self.conf.get('dhcpdefault','router'))
        #self.dns.start()
    
    def addThreads(self,service):
        self.threadsAP.append(service)

    def killThreads(self):
        if not len(self.Apthreads['RogueAP']) > 0:
            return

        self.proxy.Stop()
        self.mitmhandler.Stop()
        self.dnsserver.Stop()
        self.dhcpcontrol.Stop()
        self.wireless.Stop()

        self.conf.set('accesspoint', 'statusAP',False)
        for thread in self.Apthreads['RogueAP']:
            if thread is not None:
                if (isinstance(thread, list)):
                    for sub_thread in thread:
                        if (sub_thread != None):
                            sub_thread.stop()
                    continue
                thread.stop()

        for line in self.wireless.Activated.getSettings().SettingsAP['kill']: exec_bash(line)
        self.Apthreads['RogueAP'] = []

    def countThreads(self):
        return len(self.threadsAP['RougeAP'])

    def do_ignore(self, args):
        ''' the message logger will be ignored '''
        logger  = self.logger_manager.get(args)
        if (logger != None):
            return logger.setIgnore(True)
        print(display_messages('Logger class not found.', error=True))

    def do_clients(self, args):
        ''' show all clients connected on AP '''
        self.ui_table.start()
        self.addThreads(self.ui_table)
        # App = TestApp()
        # App.run()

    def do_monitor(self, args):
        ''' monitor traffic capture realtime Sniffer'''
        self.ui_monitor.start()
        self.addThreads(self.ui_monitor)

    def do_stop(self,args):
        ''' stop access point '''
        self.killThreads()


    def do_info(self, args):
        ''' show all variable for settings AP'''
        print(display_messages('Settings Access Point:',info=True,sublime=True))
        for item in self.commands.keys():
            print('{} = {} '.format(item, self.conf.get('accesspoint',self.commands[item])))
        print('\n')
        

    def do_set(self, args):
        ''' set variable for access point '''
        try:
            command,value = args.split()[0],args.split()[1]
            if (command in self.commands.keys()):
                self.conf.set('accesspoint',self.commands[command],value)
                print(display_messages('{} changed to => {}'.format(command, value),sucess=True))
            else:
                print(display_messages('unknown command: {} '.format(command),error=True))
        except IndexError:
            pass
    
    # def do_show(self, args):
    #     print(display_messages('Plugins:',info=True,sublime=True))
    #     for plugin in self.conf.get_all_childname('plugins'):
    #         if ('_plugin' in plugin):
    #             print('{0:20} = {1}'.format(plugin,
    #             self.getColorStatusPlugins(self.conf.get('plugins',plugin,format=bool))))
    #     pass

    def do_plugins(self, args=str):
        ''' show/edit all plugins abaliable for attack '''
        if (len(args.split()) > 0):
            try:
                plugin_name,plugin_status = list(args.split())[0],list(args.split())[1]
                if (plugin_status not in ['true','false','True','False']):
                    return print(display_messages('wifipumpkin-ng: error: unrecognized arguments {}'.format(plugin_status),error=True))
                if (plugin_name in self.conf_pproxy.get_all_childname('plugins')):
                    return self.conf_pproxy.set('plugins',plugin_name, plugin_status)
                return print(display_messages('plugin {} not found'.format(plugin_name),error=True))
            except IndexError:
                return self.help_plugins()
        print(display_messages('PumpkinProxy plugins:',info=True,sublime=True))
        for plugin in self.conf_pproxy.get_all_childname('plugins'):
            print('{0:20} = {1}'.format(plugin,
            self.getColorStatusPlugins(self.conf_pproxy.get('plugins',
            plugin,format=bool))))
        print('\n')
    
    def help_plugins(self):
        print('\n'.join([ 'usage: plugins [module name ] [(True/False)]',
                    'wifipumpkin-ng: error: unrecognized arguments',
                    ]))

    def getColorStatusPlugins(self, status):
        if (status): 
            return setcolor(status,color='green')
        return setcolor(status,color= 'red')


    def complete_ignore(self, text, args, start_index, end_index):
        if text:
            return [command for command in self.logger_manager.all()
                    if command.startswith(text)]
        else:
            return list(self.logger_manager.all())

    def complete_set(self, text, args, start_index, end_index):
        if text:
            return [command for command in self.commands.keys()
                    if command.startswith(text)]
        else:
            return list(self.commands.keys())

    def complete_plugins(self, text, args, start_index, end_index):
        if (text):
            return [command for command in self.conf_pproxy.get_all_childname('plugins') if 
            command.startswith(text)]
        else:
            return self.conf_pproxy.get_all_childname('plugins')

    def do_exit(self, args):
        ''' exit program and all threads'''
        self.killThreads()
        print('Exiting...')
        raise SystemExit
