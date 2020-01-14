#from core.widgets.docks.dock import *
from core.controls.threads import  ProcessThread
from core.controllers.wirelessmodecontroller import AccessPointSettings
from core.common.uimodel import *
from core.widgets.docks.dock import *
from core.common.platforms import setup_logger
from core.config.globalimport import *
from core.widgets.default.logger_manager import LoggerManager

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


    def __init__(self,parent):
        super(ProxyMode, self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        #self.server = ThreadReactor()
        #setup_logger(self.Name,self.LogFile,self.parent.currentSessionID)
        #self.logger  = getLogger(self.Name)
        self.handler = None
        self.reactor = None
        self.subreactor = None
        self.search = {
            'sslstrip': str('iptables -t nat -A PREROUTING -p tcp' +
                            ' --destination-port 80 -j REDIRECT --to-port ' + self.conf.get('settings','redirect_port')),
            'dns2proxy': str('iptables -t nat -A PREROUTING -p udp --destination-port 53 -j REDIRECT --to-port 53'),
            'bdfproxy': str('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080'),
            'PumpkinProxy': str('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080')
            }

        self.search[self.Name]=self.iptablesrules



        #self.controlui.clicked.connect(self.CheckOptions)
        #self.setEnabled(self.FSettings.Settings.get_setting('plugins', self.Name, format=bool))
        #self.dockwidget = Dockable(None,title=self.Name)

        self.loggermanager = LoggerManager.getInstance()
        self.configure_logger()

    def configure_logger(self):
        config_extra  = self.loggermanager.getExtraConfig(self.ID)
        config_extra['extra']['session'] = self.parent.currentSessionID

        self.logger = StandardLog(self.ID, 
            colorize=self.conf.get('settings', 'log_colorize', format=bool), 
            serialize=self.conf.get('settings', 'log_serialize', format=bool), 
        config=config_extra)
        self.logger.filename = self.LogFile
        self.loggermanager.add( self.ID, self.logger)


    def getTypePlugin(self):
        return self.TypePlugin
    
    def setTypePlugin(self, type_plugin):
        self.TypePlugin = type_plugin

    def setID(self, id):
        self.ID = id

    def isChecked(self):
        return self.conf.get('plugins', self.ID, format=bool)

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
        self._cmd_array.extend(self.parent.currentSessionID)
        return  self._cmd_array

    def boot(self):
        self.reactor= ProcessThread({'python': self.CMD_ARRAY})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.Name)

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
        if self.FSettings.Settings.get_setting('accesspoint', 'statusAP', format=bool):
            try:
                data = str(data).split(' : ')[1]
                for line in data.split('\n'):
                    if len(line) > 2 and not self.parent.currentSessionID in line:
                        self.dockwidget.writeModeData(line)
                        self.logger.info(line)
            except IndexError:
                return None

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
