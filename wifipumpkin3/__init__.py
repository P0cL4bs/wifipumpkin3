from wifipumpkin3.core.common.terminal import ConsoleUI
from wifipumpkin3.core.common.defaultwidget import *
from wifipumpkin3.core.config.globalimport import *

from wifipumpkin3.core.controllers.wirelessmodecontroller import *
from wifipumpkin3.core.controllers.dhcpcontroller import *
from wifipumpkin3.core.controllers.proxycontroller import *
from wifipumpkin3.core.controllers.mitmcontroller import *
from wifipumpkin3.core.controllers.dnscontroller import *
from wifipumpkin3.core.controllers.uicontroller import *

from wifipumpkin3.modules import *
from wifipumpkin3.modules import module_list, all_modules

approot = QtCore.QCoreApplication.instance()

class PumpkinShell(Qt.QObject, ConsoleUI):
    """
    :parameters
        options : parse_args
    """
    instances=[]
    _all_modules = None

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    def __init__(self, parse_args):
        self.__class__.instances.append(weakref.proxy(self))
        self.parse_args = parse_args

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

        self.parser_list_func = {
            #parser_set_proxy is default extend class 
            'parser_set_proxy' : self.proxy.pumpkinproxy,
            'parser_set_plugin': self.mitmhandler.sniffkin3,
            'parser_set_mode': self.wireless.Settings,
        }
        self.parser_complete_plugin = {}

        # hook function (plugins and proxys)
        self.intialize_hook_func(self.proxy)
        self.intialize_hook_func(self.mitmhandler)

        self.commands = \
        {
            'interface': 'interfaceAP',
            'ssid': 'ssid',
            'bssid': 'bssid',
            'channel':'channel', 
            'proxy': 'proxy_plugins',
            'plugin': 'plugin',
            'mode': 'mode',
        }
        for plugin_name, plugins_info in self.proxy.getInfo().items():
            self.commands[plugin_name]  = ''
        for plugin_name, plugins_info in self.mitmhandler.getInfo().items():
            self.commands[plugin_name]  = ''
        for mode_name, mode_info in self.wireless.getAllModeInfo.items():
            self.commands[mode_name]  = ''
        

        self.Apthreads = {'RogueAP': [], 'ControllersAP' : []}

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

    def intialize_hook_func(self, controller):
        # load all parser funct and plguins command CLI for plugins
        for plugin_name in controller.getInfo():
            self.parser_list_func['parser_set_' + plugin_name] = getattr(controller, plugin_name) 
            if (getattr(controller, plugin_name).getPlugins != None):
                self.parser_complete_plugin['parser_set_' + plugin_name] = getattr(controller, plugin_name).getPlugins

    def do_show(self, args):
        """ show available modules"""
        headers_table, output_table = ["Name", "Description"], []
        print(display_messages('Available Modules:',info=True,sublime=True))
        for name,module in self.all_modules.items():
            output_table.append([name, getattr(module, "ModPump").__doc__])
        return display_tabulate(headers_table, output_table)

    def do_mode(self, args):
        """ all wireless mode available """
        headers_table, output_table = ["ID","Activate","Description"], []
        print(display_messages('Available Wireless Mode:',info=True,sublime=True))
        for id_mode,info in self.wireless.getAllModeInfo.items():
            output_table.append([id_mode, setcolor('True',color='green') if 
                    info['Checked']  else setcolor('False',color='red'),info['Name']])
        return display_tabulate(headers_table, output_table)

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
        self.Apthreads['ControllersAP'].append(self.dhcpcontrol)
        self.Apthreads['ControllersAP'].append(self.dnsserver)
        self.Apthreads['ControllersAP'].append(self.proxy)
        self.Apthreads['ControllersAP'].append(self.mitmhandler)

        for controller in self.Apthreads['ControllersAP']:
            controller.Start()
        self.Apthreads['ControllersAP'].append(self.wireless)

        self.Apthreads['RogueAP'].insert(0,self.wireless.ActiveReactor)
        self.Apthreads['RogueAP'].insert(1,self.dhcpcontrol.ActiveReactor)
        self.Apthreads['RogueAP'].insert(2,self.dnsserver.ActiveReactor)
        self.Apthreads['RogueAP'].extend(self.proxy.ActiveReactor)
        self.Apthreads['RogueAP'].extend(self.mitmhandler.ActiveReactor)

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

    def do_jobs(self, args):
        """ show all threads/processes in background """
        if len(self.Apthreads['RogueAP']) > 0:
            process_background = {}
            headers_table, output_table = ["ID", "PID"], []
            for controller in self.Apthreads['ControllersAP']:
                process_background.update(controller.getReactorInfo())

            for id_controller, info in process_background.items():
                output_table.append([info['ID'], info['PID']])
                
            print(display_messages('Background processes/threads:',info=True,sublime=True))
            return display_tabulate(headers_table, output_table)
        print(display_messages('the AccessPoint is not running',info=True))
        

    def do_info(self, args):
        """ get info from the module/plugin""" 
        try:
            command = args.split()[0]
            plugins = self.mitmhandler.getInfo().get(command)
            proxys = self.proxy.getInfo().get(command)
            if plugins or proxys:
                print(display_messages('Information {}: '.format(command),info=True,sublime=True))
            if plugins:
                for name,info in plugins.items():
                    if (name != 'Config'):
                        print(' {} : {}'.format(setcolor(name,color='blue'), 
                        setcolor(info,color='yellow')))
            if proxys:
                for name,info in proxys.items():
                    if (name != 'Config'):
                        print(' {} : {}'.format(setcolor(name,color='blue'), 
                        setcolor(info,color='yellow')))
            
            if plugins or proxys:
                print('\n')

        except IndexError:
            pass

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
            setcolor('is Running',color='green') if status_ap  else setcolor('not Running',color='red')])
        return display_tabulate(headers_table, output_table)

    def do_set(self, args):
        ''' set variable proxy,plugin and access point '''
        try:
            command,value = args.split()[0],args.split()[1]
            for func in self.parser_list_func:
                if command in func:
                    return getattr(self.parser_list_func[func], func)(value, args)
            # hook function configure plugin 
            for plugin in self.parser_complete_plugin:
                if command in self.parser_complete_plugin[plugin]:
                    return getattr(self.parser_list_func[plugin], plugin)(value, command)

            if (command in self.commands.keys()):
                self.conf.set('accesspoint',self.commands[command],value)
                print(display_messages('changed {} to => {}'.format(command, value),sucess=True))
            else:
                print(display_messages('unknown command: {} '.format(command),error=True))
        except IndexError:
            pass

    def do_proxys(self, args):
        ''' show all proxys available for attack  '''
        headers_table, output_table = ["Proxy", "Active", 'Port', 'Description'], []
        plugin_info_activated = None
        config_instance = None
        headers_plugins, output_plugins = ["Name", "Active"], []

        for plugin_name, plugin_info in self.proxy.getInfo().items():
            status_plugin = self.conf.get('proxy_plugins',plugin_name, format=bool)
            # save plugin activated infor
            if (plugin_info['Config'] != None):
                if (self.conf.get_name_activated_plugin('proxy_plugins') == plugin_name):
                    plugin_info_activated = plugin_info
                    config_instance = plugin_info_activated['Config']

            output_table.append(
            [
                plugin_name,setcolor('True',color='green') if 
                    status_plugin  else setcolor('False',color='red'),
                plugin_info['Port'],
                plugin_info['Description'][:50] + '...' if len(plugin_info['Description']) > 50 else 
                plugin_info['Description']
            ]) 

        print(display_messages('Available Proxys:',info=True,sublime=True))
        display_tabulate(headers_table, output_table)
        # check plugin none
        if not plugin_info_activated: return
        # check if plugin selected is iquals the plugin config
        if (plugin_info_activated['ID'] != self.conf.get_name_activated_plugin('proxy_plugins')):
            return 
        all_plugins = plugin_info_activated['Config'].get_all_childname('plugins')
        for plugin_name in all_plugins:
            status_plugin = config_instance.get('plugins', plugin_name,format=bool )
            output_plugins.append(
            [
                plugin_name,
                setcolor('True',color='green') if status_plugin
                 else setcolor('False',color='red')
            ])
        print(display_messages('{} plugins:'.format(plugin_info_activated['Name']),info=True,sublime=True))
        return display_tabulate(headers_plugins, output_plugins)


    def do_plugins(self, args=str):
        ''' show all plugins available for attack '''
        headers_table, output_table = ["Name", "Active", "Description"], []
        headers_plugins, output_plugins = ["Name", "Active"], []
        all_plugins,config_instance = None, None
        for plugin_name, plugin_info in self.mitmhandler.getInfo().items():
            status_plugin = self.conf.get('mitm_modules',plugin_name, format=bool)
            output_table.append(
            [   plugin_name,setcolor('True',color='green') if 
                    status_plugin  else setcolor('False',color='red'),
                plugin_info['Description'][:50] + '...' if len(plugin_info['Description']) > 50 else 
                plugin_info['Description']
            ])   
            if (self.mitmhandler.getInfo()[plugin_name]['Config'] !=  None and status_plugin):
                config_instance = self.mitmhandler.getInfo()[plugin_name]['Config']
                all_plugins = self.mitmhandler.getInfo()[plugin_name]['Config'].get_all_childname('plugins')
        
        print(display_messages('Available Plugins:',info=True,sublime=True))
        display_tabulate(headers_table, output_table)

        if not all_plugins: return

        for plugin_name in all_plugins:
            status_plugin = config_instance.get('plugins', plugin_name,format=bool )
            output_plugins.append(
            [
                plugin_name,
                setcolor('True',color='green') if status_plugin
                 else setcolor('False',color='red')
            ])
        print(display_messages('Sniffkin3 plugins:',info=True,sublime=True))
        return display_tabulate(headers_plugins, output_plugins)

    def help_plugins(self):
        print('\n'.join([ 'usage: set plugin [module name ] [(True/False)]',
                    'wifipumpkin-ng: error: unrecognized arguments',
                    ]))

    def getColorStatusPlugins(self, status):
        if (status): 
            return setcolor(status,color='green')
        return setcolor(status,color= 'red')


    def complete_info(self, text, args, start_index, end_index):
        if text:
            return [command for command in list(self.commands.keys())
                    if command.startswith(text)]
        else:
            return list(self.commands.keys())

    def complete_ignore(self, text, args, start_index, end_index):
        if text:
            return [command for command in self.logger_manager.all()
                    if command.startswith(text)]
        else:
            return list(self.logger_manager.all())

    def complete_set(self, text, args, start_index, end_index):
        if text:
            command_list = []
            for func in self.parser_complete_plugin:
                if text.startswith(func.split('_set_')[1]):
                    for command in self.parser_complete_plugin[func]:
                        if command.startswith(text):
                            command_list.append(command)

            for command in self.commands:
                if command.startswith(text):
                    command_list.append(command)
            return command_list
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
