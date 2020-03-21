from wifipumpkin3.core.common.accesspoint import AccessPoint
#from core.common.sniffing import SniffingPackets
from wifipumpkin3.core.common.terminal import ConsoleUI
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants  as C
from wifipumpkin3.core.utility.printer import display_messages,setcolor
from termcolor import colored
import npyscreen, threading
from tabulate import tabulate

from wifipumpkin3.core.common.defaultwidget import *
from wifipumpkin3.core.config.globalimport import *

from wifipumpkin3.core.controllers.wirelessmodecontroller import *
from wifipumpkin3.core.controllers.dhcpcontroller import *
from wifipumpkin3.core.servers.dhcp.dhcp import *
from wifipumpkin3.core.controllers.proxycontroller import *
from wifipumpkin3.core.controllers.mitmcontroller import *
from wifipumpkin3.core.controllers.dnscontroller import *
from wifipumpkin3.core.controllers.uicontroller import *

from wifipumpkin3.modules import *
from wifipumpkin3.modules import module_list, all_modules

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
    _all_modules =None

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    def __init__(self, parse_args):
        self.__class__.instances.append(weakref.proxy(self))
        self.parse_args = parse_args
        self.parser_list_func = {'parser_set_proxy' : self, 'parser_set_plugin': self }
        self.all_modules = module_list
        self.currentSessionID = self.parse_args.session
        super(PumpkinShell, self).__init__(parse_args=self.parse_args)

    def initialize_core(self):
        """ this method is called in __init__ """
        self.coreui = DefaultWidget(self)
        self.wireless = WirelessModeController(self)
        self.dhcpcontrol = DHCPController(self)
        self.dnsserver = DNSController(self)
        self.tableUI = UIController(self)
        self.logger_manager = LoggerManager.getInstance()

        self.proxy = self.coreui.Plugins.Proxy
        self.mitmhandler = self.coreui.Plugins.MITM

        self.commands = \
        {
            'interface': 'interfaceAP',
            'ssid': 'ssid',
            'bssid': 'bssid',
            'channel':'channel', 
            'proxy': 'proxy_plugins',
            'plugin': 'plugin',
        }
        for plugin_name, plugins_info in self.proxy.getInfo().items():
            self.commands[plugin_name]  = ''
        for plugin_name, plugins_info in self.mitmhandler.getInfo().items():
            self.commands[plugin_name]  = ''

        self.Apthreads = {'RogueAP': []}

    @property
    def all_modules(self):
        return self._all_modules

    @all_modules.setter
    def all_modules(self, module_list):
        m_avaliable = {}
        for name,module in module_list().items():
            if (hasattr(module, "ModPump")):
                m_avaliable[name] = module
        self._all_modules =  m_avaliable

    def do_show(self, args):
        """ show available modules"""
        headers_table, output_table = ["Name", "Description"], []
        print(display_messages('Available Modules:',info=True,sublime=True))
        for name,module in self.all_modules.items():
            output_table.append([name, getattr(module, "ModPump").__doc__])
        print(tabulate(output_table, headers_table, tablefmt="simple"))
        print("\n")

    def do_use(self, args):
        """ select module for modules"""
        if (args in self.all_modules.keys()):
            module = module_list()[args].ModPump(self.parse_args, globals())
            module.cmdloop()
        
    def getAccessPointStatus(self,status):
        self.ui_table.startThreads()
        self.ui_monitor.startThreads()


    def do_start(self,args):
        ''' start access point '''

        self.interfaces = Linux.get_interfaces()
        if (not self.conf.get("accesspoint", self.commands['interface']) in self.interfaces.get('all')):
            print(display_messages('The interface not found! ',error=True))
            sys.exit(1)

        self.conf.set('accesspoint',self.commands['interface'],self.parse_args.interface)
        self.conf.set('accesspoint','current_session',self.parse_args.session)

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

    def do_restore(self, args):
        ''' the message logger will be restored '''
        logger  = self.logger_manager.get(args)
        if (logger != None):
            return logger.setIgnore(False)
        print(display_messages('Logger class not found.', error=True))

    def do_clients(self, args):
        ''' show all clients connected on AP '''
        self.tableUI.ui_table_mod.start()

    def do_stop(self,args):
        ''' stop access point '''
        self.killThreads()


    def do_info_ap(self, args):
        ''' show all variable and status for settings AP '''
        headers_table, output_table = ["BSSID", "SSID", "Channel", "Iface", "StatusAP"], []
        print(display_messages('Settings AccessPoint:',info=True,sublime=True))
        status_ap =self.conf.get('accesspoint',"statusAP", format=bool)
        output_table.append([
            self.conf.get('accesspoint',self.commands["bssid"]),
            self.conf.get('accesspoint',self.commands["ssid"]),
            self.conf.get('accesspoint',self.commands["channel"]),
            self.conf.get('accesspoint',self.commands["interface"]),
            setcolor('Yes',color='green') if status_ap  else setcolor('False',color='red')])
        print(tabulate(output_table, headers_table,tablefmt="simple"))
        print('\n')

    def do_set(self, args):
        ''' set variable for access point '''
        try:
            command,value = args.split()[0],args.split()[1]
            for func in self.parser_list_func:
                if command in func:
                    return getattr(self.parser_list_func[func], func)(value, args)
            if (command in self.commands.keys()):
                self.conf.set('accesspoint',self.commands[command],value)
                print(display_messages('changed {} to => {}'.format(command, value),sucess=True))
            else:
                print(display_messages('unknown command: {} '.format(command),error=True))
        except IndexError:
            pass

    def parser_set_proxy(self, proxy_name, *args):
        if not self.conf.get('accesspoint', 'statusAP') or len(self.Apthreads['RogueAP']) == 0:
            plugins_selected = [plugin for plugin in self.conf.get_all_childname('proxy_plugins') if plugin == proxy_name]
            if (plugins_selected != []):
                self.conf.set('proxy_plugins', plugins_selected[0], True)
                for proxy in self.conf.get_all_childname('proxy_plugins'):
                    if proxy != plugins_selected[0]:
                        self.conf.set('proxy_plugins', proxy, False)
                return
            return print(display_messages('unknown command: {} '.format(proxy_name),error=True))
        print(display_messages('Error: 0x01 - the AP(access point) is running',error=True))

    def do_proxys(self, args):
        ''' show all proxys available for attack  '''
        headers_table, output_table = ["Proxy", "Active", 'Port', 'Description'], []
        for plugin_name, plugin_info in self.proxy.getInfo().items():
            status_plugin = self.conf.get('proxy_plugins',plugin_name, format=bool)
            output_table.append(
            [
                plugin_name,setcolor('Yes',color='green') if 
                    status_plugin  else setcolor('False',color='red'),
                plugin_info['Port'],
                plugin_info['Description'][:50] + '...'
            ]) 

        print(display_messages('Available Proxys:',info=True,sublime=True))
        print(tabulate(output_table, headers_table,tablefmt="simple"))
        print('\n')

    def parser_set_plugin(self, proxy_name, args):
        try:
            plugin_name,plugin_status = list(args.split())[1],list(args.split())[2]
            if (plugin_status not in ['true','false','True','False']):
                return print(display_messages('wifipumpkin3: error: unrecognized arguments {}'.format(plugin_status),error=True))
            if (plugin_name in self.conf.get_all_childname('mitm_modules')):
                return self.conf.set('mitm_modules',plugin_name, plugin_status)
            return print(display_messages('plugin {} not found'.format(plugin_name),error=True))
        except IndexError:
            return self.help_plugins()


    def do_plugins(self, args=str):
        ''' show/edit all plugins available for attack '''
        headers_table, output_table = ["Name", "Active", "Description"], []
        for plugin_name, plugin_info in self.mitmhandler.getInfo().items():
            status_plugin = self.conf.get('mitm_modules',plugin_name, format=bool)
            output_table.append(
            [   plugin_name,setcolor('Yes',color='green') if 
                    status_plugin  else setcolor('False',color='red'),
                plugin_info['Description'][:50] + '...'
            ])   

        print(display_messages('Available Plugins:',info=True,sublime=True))
        print(tabulate(output_table, headers_table,tablefmt="simple"))
        print('\n')

    def help_plugins(self):
        print('\n'.join([ 'usage: set plugin [module name ] [(True/False)]',
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

    def complete_use(self, text, args, start_index, end_index):
        if (text):
            return [command for command in list(self.all_modules.keys()) if 
            command.startswith(text)]
        else:
            return list(self.all_modules.keys())

    def do_exit(self, args):
        ''' exit program and all threads'''
        self.killThreads()
        print('Exiting...')
        raise SystemExit
