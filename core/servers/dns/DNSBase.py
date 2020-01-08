import weakref
from core.config.globalimport import *
from core.common.uimodel import *
#from core.widgets.default.SessionConfig import SessionConfig
from core.utility.component import ComponentBlueprint
from core.controls.threads import (ProcessThread)
from core.common.platforms import setup_logger


class DNSBase(QtCore.QObject,ComponentBlueprint):
    Name = "DNSBaseClass"
    ID = "DNSBase"
    Author = "Dev"
    ConfigRoot="DNSServer"
    ExecutableFile = ""
    hasPreference = False
    arguments =[['label','switch','type','defaultvalue','enabled','required'],
                ]

    addDock = QtCore.pyqtSignal(object)
    def __init__(self,parent,**kwargs):
        super(DNSBase,self).__init__(parent)
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        #self.SessionConfig = SessionConfig.getInstance()
        self.reactor = None
        self.LogFile ="logs/AccessPoint/{}.log".format(self.ID)

        setup_logger(self.Name, self.LogFile, self.parent.currentSessionID)
        self.logger = getLogger(self.Name)


        # self.btnsettings.clicked.connect(self.showarguments)
        # self.btnsettings.setMaximumWidth(100)
        # self.btnsettings.setMaximumHeight(30)
        # self.controlui = QtGui.QRadioButton("{}".format(self.Name))
        # self.controlui.toggled.connect(self.controluiCallback)
        # self.controlui.setChecked(self.FSettings.Settings.get_setting(self.ConfigRoot,self.ID,format=bool))
        # self.controluiCallback()

    def isChecked(self):
        return self.conf.get('accesspoint', self.ID, format=bool)

    @property
    def commandargs(self):
        pass

    @property
    def command(self):
        cmdpath = os.popen('which {}'.format(self.ExecutableFile)).read().split('\n')[0]
        if cmdpath:
            return cmdpath
        else:
            return None

    def boot(self):
        self.reactor = ProcessThread({self.command: self.commandargs})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.Name)  # use dns2proxy as DNS server

    def LogOutput(self,data):
        if self.conf.get('accesspoint', 'statusAP', format=bool):
            try:
                data = str(data).split(' : ')[1]
                for line in data.split('\n'):
                    if len(line) > 2 and not self.parent.currentSessionID in line:
                        print(line)
                    self.logger.info(line)
            except IndexError:
                return None


class DNSSettings(CoreSettings):
    Name = "DNS Server"
    ID = "DNSSettings"
    Category = "DNS"
    instances =[]

    def __init__(self,parent=None):
        super(DNSSettings,self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__
        
        self.dnslist = [dns(self.parent) for dns in DNSBase.__subclasses__()]
        # for dns in self.dnslist:
        #     if dns.hasPreference:
        #         self.forml.addRow(dns.controlui,dns.btnsettings)
        #     else:
        #         self.forml.addRow(dns.controlui)

    @classmethod
    def getInstance(cls):
        return cls.instances[0]


