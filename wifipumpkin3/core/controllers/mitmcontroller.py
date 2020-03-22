from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.servers.mitm import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.component import ControllerBlueprint


class MitmController(PluginsUI,ControllerBlueprint):
    Name = "MITM"
    Caption = "Activity Monitor"
    mitmhandler = {}
    SetNoMitmMode = QtCore.pyqtSignal(object)
    mitm_infor = {}

    def __init__(self,parent = None,**kwargs):
        super(MitmController, self).__init__(parent)
        self.parent=parent
        self.conf = SuperSettings.getInstance()
        #self.uplinkIF = self.parent.Refactor.get_interfaces()
        #self.downlinkIF = self.parent.WLANCard.currentText()
        __manipulator= [prox(parent=self.parent) for prox in mitmmode.MitmMode.__subclasses__()]
        #Keep Proxy in a dictionary
        for k in __manipulator:
            #print(k.Name, 'mitmcontroller')
            self.mitmhandler[k.Name]=k
            self.mitm_infor[k.ID] = {
                'ID': k.ID,
                'Name' : k.Name,
                'Description': k.Description,
                'Config' : k.getConfig
            }

        self.m_name = []
        self.m_desc = []
        self.m_settings = []
        for n,p in self.mitmhandler.items():
            # self.m_name.append(p.controlui)
            # self.m_settings.append(p.btnChangeSettings)
            # self.m_desc.append(p.controlui.objectName())
            #self.manipulatorGroup.addButton(p.controlui)
            setattr(self,p.ID,p)
            #self.parent.LeftTabBar.addItem(p.tabinterface)
            #self.parent.Stack.addWidget(p)

        self.MitmModeTable = OrderedDict(
            [('Activity Monitor', self.m_name),
             ('Settings', self.m_settings),
             ('Description', self.m_desc)
             ])

    def DisableMitmMode(self,status):
        self.SetNoMitmMode.emit(status)

    def dockUpdate(self,add=True):
        self.dockMount.emit(add)

    @property
    def ActiveDock(self):
        manobj = []
        for manip in self.Active:
            manobj.append(manip.dockwidget)
        return manobj

    @property
    def Active(self):
        manobj =[]
        for manip in self.mitmhandler.values():
            if manip.isChecked():
                manobj.append(manip)
        return manobj

    @property
    def ActiveReactor(self):
        reactor=[]
        for i in self.Active:
            reactor.append(i.reactor)
        return reactor

    @property
    def get(self):
        return self.mitmhandler

    def getInfo(self):
        return self.mitm_infor

    @classmethod
    def disable(cls, val=True):
        pass

    @property
    def disableproxy(self, name):
        pass

    def Start(self):
        for i in self.Active:
            i.boot()

    def Stop(self):
        for i in self.Active:
            i.shutdown()
