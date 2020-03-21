from wifipumpkin3.core.controls.threads import  (
    ProcessThread
)
from wifipumpkin3.core.widgets.docks.dock import DockableWidget
from wifipumpkin3.core.controllers.wirelessmodecontroller import AccessPointSettings
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.widgets.default.logger_manager import LoggerManager

class Widget(Qt.QObject):
    def __init__(self,parent):
        Qt.QObject.__init__(self,parent)
class VBox(Qt.QObject):
    def __init__(self):
        Qt.QObject.__init__(self)

class MitmDock(DockableWidget):
    id = "Generic"
    title = "Generic"

    def __init__(self,parent=0,title="",info={}):
        super(MitmDock,self).__init__(parent,title,info)
        self.setObjectName(self.title)


class MitmMode(Widget):
    Name = "Generic"
    ID = "Generic"
    Author = "Wahyudin Aziz"
    Description = "Generic Placeholder for Attack Scenario"
    LogFile = C.LOG_ALL
    ModSettings = False
    ModType = "proxy" # proxy or server
    Hidden = True
    _cmd_array = []
    plugins = []
    sendError = QtCore.pyqtSignal(str)
    sendSingal_disable = QtCore.pyqtSignal(object)

    def __init__(self,parent=None):
        super(MitmMode, self).__init__(parent)
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self.reactor = None
        self.server = None
        
        #setup_logger(self.Name, self.LogFile, self.parent.currentSessionID)
        #self.logger = getLogger(self.Name)
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

    def getModType(self):
        return self.ModType
    
    def setModType(self, type_plugin):
        self.ModType = type_plugin

    def setID(self, id):
        self.ID = id

    def isChecked(self):
        return self.conf.get('mitm_modules', self.ID, format=bool)

    @property
    def CMD_ARRAY(self):
        return self._cmd_array

    @property
    def Wireless(self):
        return AccessPointSettings.instances[0]

    @property
    def hasSettings(self):
        return self.ModSettings

    def CheckOptions(self):
        self.FSettings.Settings.set_setting('mitmhandler', self.Name, self.controlui.isChecked())
        self.dockwidget.addDock.emit(self.controlui.isChecked())
        if self.ModSettings:
            self.btnChangeSettings.setEnabled(self.controlui.isChecked())
        if self.controlui.isChecked() == True:
            self.setEnabled(True)
        else:
            self.setEnabled(False)
        self.Initialize()

    def Initialize(self):
        self.SetRules()

    def SetRules(self):
        pass

    def ClearRules(self):
        pass

    def Configure(self):
        self.ConfigWindow.show()

    def boot(self):
        if self.CMD_ARRAY:
            self.reactor= ProcessThread({'python': self.CMD_ARRAY})
            self.reactor._ProcssOutput.connect(self.LogOutput)
            self.reactor.setObjectName(self.Name)

    def shutdown(self):
        if self.reactor is not None:
            self.reactor.stop()
            if hasattr(self.reactor, 'wait'):
                if not self.reactor.wait(msecs=500):
                    self.reactor.terminate()

    def LogOutput(self,data):
        #self.dockwidget.writeModeData(line)
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            self.logger.info(data)
        # if self.FSettings.Settings.get_setting('accesspoint', 'statusAP', format=bool):
        #     try:
        #         data = str(data).split(' : ')[1]
        #         for line in data.split('\n'):
        #             if len(line) > 2 and not self.parent.currentSessionID in line:
        #                 self.dockwidget.writeModeData(line)
        #                 self.logger.info(line)
        #     except IndexError:
        #         return None




