from core.common.accesspoint import AccessPoint
from core.common.sniffing import SniffingPackets
from core.common.terminal import ConsoleUI
from core.widgets.window import ui_TableMonitorClient,ui_MonitorSniffer
from core.utility.collection import SettingsINI
import core.utility.constants  as C
from core.utility.printer import display_messages
from termcolor import colored

class PumpkinShell(ConsoleUI):
    """
    :parameters
        options : parse_args
    """
    def __init__(self,options):
        ConsoleUI.__init__(self)
        self.options    = options
        self.sniffs     = SniffingPackets(self)
        self.conf       = SettingsINI(C.CONFIG_INI)
        self.conf_pproxy    = SettingsINI(C.CONFIG_PP_INI)
        self.conf_tproxy    = SettingsINI(C.CONFIG_TP_INI)
        self.ac         = AccessPoint(self)
        self.ac.sendStatusPoint.connect(self.getAccessPointStatus)
        self.ui_table   = ui_TableMonitorClient(self)
        self.ui_monitor = ui_MonitorSniffer(self)
        self.commands = {'interface': 'interfaceAP','ssid': 'ssid',
        'bssid': 'bssid','channel':'channel'}
        self.threadsAP = []
        self.setOptions()

    def setOptions(self):
        self.conf.set('accesspoint',self.commands['interface'],self.options.interface)
        self.conf.set('accesspoint','current_session',self.options.session)
        
    def getAccessPointStatus(self,status):
        self.ui_table.startThreads()
        self.ui_monitor.startThreads()

    def do_start(self,args):
        ''' start access point '''
        if (not self.countThreads() > 0): 
            self.sniffs.start()
            self.ac.start()
            self.addThreads(self.sniffs)
            return self.addThreads(self.ac)
        print(display_messages('the access point is running. [{}]'.format(
            self.conf.get('accesspoint','ssid')
        ),error=True))
    
    def addThreads(self,service):
        self.threadsAP.append(service)

    def killThreads(self):
        if (self.countThreads() > 0):
            for thread in self.threadsAP:
                thread.stop()
            self.threadsAP = []

    def countThreads(self):
        return len(self.threadsAP)

    def do_clients(self, args):
        ''' show all clients connected on AP '''
        self.ui_table.start()
        self.addThreads(self.ui_table)

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
    
    def do_show(self, args):
        print(display_messages('Plugins:',info=True,sublime=True))
        for plugin in self.conf.get_all_childname('plugins'):
            if ('_plugin' in plugin):
                print('{0:20} = {1}'.format(plugin,
                self.getColorStatusPlugins(self.conf.get('plugins',plugin,format=bool))))
        pass

    def do_plugins(self, args=str):
        if (len(args.split()) > 0):
            try:
                plugin_name,plugin_status = list(args.split())[0],list(args.split())[1]
                if (plugin_status not in ['true','false','True','False']):
                    return print(display_messages('sintax command error',error=True))
                if (plugin_name in self.conf_pproxy.get_all_childname('plugins')):
                    return self.conf_pproxy.set('plugins',plugin_name, plugin_status)
                print(display_messages('plugin {} not found'.format(plugin_name),error=True))
                return
            except IndexError:
                print(display_messages('sintax command error',error=True))
            return 
        print(display_messages('PumpkinProxy plugins:',info=True,sublime=True))
        for plugin in self.conf_pproxy.get_all_childname('plugins'):
            print('{0:20} = {1}'.format(plugin,
            self.getColorStatusPlugins(self.conf_pproxy.get('plugins',
            plugin,format=bool))))
        print('\n')

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
