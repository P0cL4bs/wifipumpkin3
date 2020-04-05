from wifipumpkin3.core.config.globalimport import *
from collections import OrderedDict
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.servers.proxy import *
from wifipumpkin3.core.utility.component import ControllerBlueprint



class ProxyModeController(PluginsUI, ControllerBlueprint):
    Name = "Proxy"
    Caption = "Enable Proxy Server"
    ID = 'proxy_controller'
    proxies = {}
    proxies_infor = {}
    SetNoProxy = QtCore.pyqtSignal(object)
    dockMount = QtCore.pyqtSignal(bool)

    @staticmethod
    def getID():
        return ProxyModeController.ID

    def __init__(self,parent = None,**kwargs):
        super(ProxyModeController, self).__init__(parent)
        self.parent=parent
         # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        self.conf = SuperSettings.getInstance()

        #self.setChecked(self.conf.get('plugins', 'disableproxy', format=bool))
        #self.clicked.connect(self.get_disable_proxy)
        
        __proxlist= [prox(parent=self.parent) for prox in proxymode.ProxyMode.__subclasses__()]

        #Keep Proxy in a dictionary
        for k in __proxlist:
            self.proxies[k.Name]=k

            self.proxies_infor[k.ID] = {
                'ID': k.ID,
                'Name' : k.Name,
                'Port' : k.getRunningPort(),
                'Activate': k.isChecked(),
                'Author' : k.Author,
                'Logger' : k.LogFile,
                'ConfigPath' : k.CONFIGINI_PATH,
                'Description': k.Description,
                'Config' : k.getConfig,
            }



        self.p_name = []
        self.p_desc = []
        self.p_settings = []
        self.p_author = []
        self.NoProxy = None
        for n,p in self.proxies.items():
            if p.Name == "No Proxy":
                self.NoProxy = p
            self.p_author.append(p.Author)
            #self.p_desc.append(p.controlui.objectName())
            # if (type(p.controlui) == type(QtGui.QRadioButton()) ):
            #     self.proxyGroup.addButton(p.controlui)
            #p.sendSingal_disable.connect(self.DisableProxy)
            #p.dockwidget.addDock.connect(self.dockUpdate)
            if (hasattr(p,'ID')):
                setattr(self, p.ID, p)

        self.THeadersPluginsProxy = OrderedDict(
            [('Proxies', self.p_name),
             ('Settings', self.p_settings),
             ('Author', self.p_author),
             ('Description', self.p_desc)
             ])
        
    def isChecked(self):
        return self.conf.get('plugins', self.ID, format=bool)
        
    def get_disable_proxy(self):


        if self.isChecked():
            if self.Active.Name == "No Proxy":
                self.SetNoProxy.emit(False)
            else:

                self.parent.set_proxy_statusbar(self.Active.Name, disabled=False)
                self.FSettings.Settings.set_setting('plugins', 'disableproxy',
                                                    self.isChecked())

        else:
            self.SetNoProxy.emit(self.isChecked())
            self.FSettings.Settings.set_setting('plugins', 'disableproxy',
                                                self.isChecked())


    def dockUpdate(self,add=True):
        self.dockMount.emit(add)

    def DisableProxy(self,status):
        self.SetNoProxy.emit(status)
        
    @property
    def ActiveDocks(self):
        return self.Active.dockwidget

    @property
    def ActiveReactor(self):
        reactor = []
        for act in self.proxies.values():
            if act.isChecked():
                if act.Name == "noproxy":
                    reactor.append(act.reactor)
                    reactor.append(act.subreactor)
                else:
                    reactor.append(act.reactor)
                    if act.subreactor:
                        reactor.append(act.subreactor)
        return  reactor



    @property
    def Active(self):
        for act in self.proxies.values():
            # exclude tcp proxy log
            if act.getTypePlugin() != 2:
                #print(act.isChecked(),act.Name)
                if act.isChecked():
                    return act

    @property
    def ActiveLoad(self):
        ''' load all proxies type checkbox UI in tab plugins '''
        proxies = []
        for act in self.proxies.values():
            if act.isChecked():
                if act.Name != "No Proxy":
                    proxies.append(act)
        return  proxies

    @property
    def get(self):
        return self.proxies
    
    def getInfo(self):
        return self.proxies_infor

    @classmethod
    def disable(cls, val=True):
        pass

    @property
    def disableproxy(self, name):
        pass

    def Start(self):
        self.Active.Initialize()
        self.Active.Serve()
        self.Active.boot()
        # load proxy checkbox all type all proxies
        for proxy in self.ActiveLoad:
            if (proxy.Name != self.Active.Name):
                proxy.Initialize()
                proxy.Serve()
                proxy.boot()


    @property
    def getReactor(self):
        return self.Active.reactor
    
    def getReactorInfo(self):
        info_reactor = {}
        info_reactor[self.getReactor.getID()] = {
            'ID' : self.getReactor.getID(), 'PID' : self.getReactor.getpid()
            }
        return info_reactor

    def Stop(self):
        self.Active.Serve(False)
        self.Active.shutdown()

    def SaveLog(self):

        self.Active.SaveLog()
