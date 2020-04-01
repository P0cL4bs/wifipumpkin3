#from core.widgets.docks.dock import *
from wifipumpkin3.core.controls.threads import  ProcessThread
from wifipumpkin3.core.controllers.wirelessmodecontroller import AccessPointSettings
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.widgets.docks.dock import *
from wifipumpkin3.core.common.platforms import setup_logger
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.widgets.default.logger_manager import LoggerManager
from wifipumpkin3.core.utility.component import ComponentBlueprint

class Widget(Qt.QObject):
    def __init__(self):
        Qt.QObject.__init__(self)

class VBox(Qt.QObject):
    def __init__(self):
        Qt.QObject.__init__(self)

class ProxyMode(Widget,ComponentBlueprint):
    Name = "Generic"
    Author = "Wahyudin Aziz"
    ID = "generic"
    Description = "Generic Placeholder for Attack Scenario"
    LogFile = C.LOG_ALL
    CONFIGINI_PATH = ''
    ModSettings = False
    ModType = "proxy" # proxy or server
    EXEC_PATH = ''
    _cmd_array = []
    Hidden = True
    plugins = []
    sendError = QtCore.pyqtSignal(str)
    sendSingal_disable = QtCore.pyqtSignal(object)
    addDock=QtCore.pyqtSignal(object)
    TypePlugin = 1
    RunningPort = 80
    config = None


    def __init__(self,parent):
        super(ProxyMode, self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()

        self.handler = None
        self.reactor = None
        self.subreactor = None
        self.defaults_rules = {
            'ssslstrip': 
                [
                    'iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port ' + self.conf.get('settings','redirect_port')
                ],
            'pumpkinproxy': 
                [
                    'iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port {}'.format(self.conf.get('proxy_plugins','pumpkinproxy_config_port'))
                ]
            }
        # set config path plugin
        if (self.getConfigINIPath != ''):
            self.config = SettingsINI(self.getConfigINIPath)

        self.loggermanager = LoggerManager.getInstance()
        self.configure_logger()

    def configure_logger(self):
        if not self.Hidden:
            config_extra  = self.loggermanager.getExtraConfig(self.ID)
            config_extra['extra']['session'] = self.parent.currentSessionID

            self.logger = StandardLog(self.ID, 
                colorize=self.conf.get('settings', 'log_colorize', format=bool), 
                serialize=self.conf.get('settings', 'log_serialize', format=bool), 
            config=config_extra)
            self.logger.filename = self.LogFile
            self.loggermanager.add( self.ID, self.logger)

    def parser_set_proxy(self, proxy_name, *args):
        # default parser proxy commands complete
        if not self.conf.get('accesspoint', 'statusAP', format=bool):
            plugins_selected = [plugin for plugin in self.conf.get_all_childname('proxy_plugins') if plugin == proxy_name]
            if (plugins_selected != []):
                self.conf.set('proxy_plugins', plugins_selected[0], True)
                for proxy in self.conf.get_all_childname('proxy_plugins'):
                    if proxy != plugins_selected[0] and not '_config' in proxy:
                        self.conf.set('proxy_plugins', proxy, False)
                return
            return print(display_messages('unknown command: {} '.format(proxy_name),error=True))
        print(display_messages('Error: 0x01 - the AP(access point) is running',error=True))

    def runDefaultRules(self):
        for rules in self.defaults_rules[self.ID]:
            os.system(rules)

    @property
    def getPlugins(self):
        return None

    @property
    def getConfigINIPath(self):
        return self.CONFIGINI_PATH

    @property
    def getConfig(self):
        return self.config

    def setRunningPort(self, value):
        self.RunningPort = value

    def getRunningPort(self):
        return self.RunningPort

    def getTypePlugin(self):
        return self.TypePlugin
    
    def setTypePlugin(self, type_plugin):
        self.TypePlugin = type_plugin

    def setID(self, id):
        self.ID = id

    def isChecked(self):
        return self.conf.get('proxy_plugins', self.ID, format=bool)

    @property
    def iptablesrules(self):
        pass

    @property
    def Wireless(self):
        return AccessPointSettings.instances[0]

    def get_disable_status(self):
        if self.FSettings.Settings.get_setting('plugins', self.Name, format=bool) == True:
            if self.Name == "No Proxy":
                self.ClearRules()
                self.parent.set_proxy_statusbar('', disabled=True)
                self.sendSingal_disable.emit(self.controlui.isChecked())
                return

            self.parent.set_proxy_statusbar(self.Name)

    def onProxyEnabled(self):
        pass

    def onProxyDisabled(self):
        pass

    @property
    def hasSettings(self):
        return self.ModSettings

    def CheckOptions(self):
        self.FSettings.Settings.set_setting('plugins', self.Name, self.controlui.isChecked())
        self.dockwidget.addDock.emit(self.controlui.isChecked())
        self.get_disable_status()
        self.ClearRules()
        self.Initialize()
        if self.ModSettings:
            self.btnChangeSettings.setEnabled(self.controlui.isChecked())
        if self.controlui.isChecked() == True:
            self.setEnabled(True)
            self.onProxyEnabled()
            self.tabinterface.setText("[ {} ]".format(self.Name))

        else:
            self.onProxyDisabled()
            self.setEnabled(False)
            self.tabinterface.setText(self.Name)

    @property
    def CMD_ARRAY(self):
        #self._cmd_array.extend(self.parent.currentSessionID)
        return  self._cmd_array

    def boot(self):
        self.reactor= ProcessThread({'python3': self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

    def shutdown(self):
        pass

    @property
    def isEnabled(self):
        pass
        
    def Initialize(self):
        pass

    def optionsRules(self,type):
        ''' add rules iptable by type plugins'''
        return self.search[type]

    def SetRules(self,strrules=""):
        items = []
        for index in xrange(self.FSettings.ListRules.count()):
            items.append(str(self.FSettings.ListRules.item(index).text()))
        if self.optionsRules(strrules) in items:
            return
        if (self.optionsRules(strrules) != None):
            item = QtGui.QListWidgetItem()
            item.setText(self.optionsRules(strrules))
            item.setSizeHint(QtCore.QSize(30, 30))
            self.FSettings.ListRules.addItem(item)

    def ClearRules(self):
        for rules in self.search.keys():
            self.unset_Rules(rules)

    def LogOutput(self,data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            print(data)

    def Configure(self):
        self.ConfigWindow.show()

    def unset_Rules(self,iptables):
        ''' remove rules from Listwidget in settings widget'''
        items = []
        for index in xrange(self.FSettings.ListRules.count()):
            items.append(str(self.FSettings.ListRules.item(index).text()))
        for position,line in enumerate(items):
            if self.optionsRules(iptables) == line:
                self.FSettings.ListRules.takeItem(position)

    def SaveLog(self):
        pass

    def Serve(self,on=True):
        pass


class Dockable(DockableWidget):
    def __init__(self,parent=0,title="",info={}):
        super(Dockable,self).__init__(parent,title,info)
        self.setObjectName(title)
