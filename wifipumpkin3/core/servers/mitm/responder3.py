from wifipumpkin3.core.servers.mitm.mitmmode import MitmMode
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.widgets.docks.dock import DockableWidget
from wifipumpkin3.core.controls.threads import ProcessThread


class NetCredential(DockableWidget):
    id = "Responder3"
    title = "Responder3"
    def __init__(self,parent=None,title="",info={}):
        super(NetCredential,self).__init__(parent,title,info)
        self.setObjectName(self.title)

    def writeModeData(self,data):
        ''' get data output and add on QtableWidgets '''
        print(data)
        # self.THeaders['Username'].append(data['POSTCreds']['User'])
        # self.THeaders['Password'].append(data['POSTCreds']['Pass'])
        # self.THeaders['Url'].append(data['POSTCreds']['Url'])
        # self.THeaders['Source/Destination'].append(data['POSTCreds']['Destination'])

    def stopProcess(self):
        pass

class Responder3(MitmMode):
    #TODO: implement a module example to mitmmode
    Name = "Responder 3"
    ID = "responder3"
    Author = "PumpkinDev"
    Description = "New and improved Responder for Python3"
    LogFile = C.LOG_RESPONDER3
    ConfigMitmPath = None
    _cmd_array = []
    ModSettings = True
    ModType = "server"  # proxy or server
    config = None
    
    def __init__(self,parent,FSettingsUI=None,main_method=None,  **kwargs):
        super(Responder3, self).__init__(parent)
        self.setID(self.ID)
        self.setModType(self.ModType)
        self.dockwidget = NetCredential(None,title=self.Name)

    @property
    def CMD_ARRAY(self):
        iface  = self.conf.get('accesspoint', 'interfaceAP')
        config_responder3_path = self.conf.get('mitm_modules', 'responder3_config')
        self._cmd_array=['-I',iface , '-4', '-p', config_responder3_path]
        return self._cmd_array

    def boot(self):
        if self.CMD_ARRAY:
            self.reactor= ProcessThread({'responder3': self.CMD_ARRAY})
            self.reactor._ProcssOutput.connect(self.LogOutput)
            self.reactor.setObjectName(self.Name)


    def parser_set_responder3(self, status, plugin_name):
        try:
            # plugin_name = pumpkinproxy.no-cache 
            name_plugin,key_plugin = plugin_name.split('.')[0],plugin_name.split('.')[1]
            if key_plugin in self.config.get_all_childname('plugins'):
                self.config.set('plugins',key_plugin, status)
                print(display_messages('responder3: {} status: {}'.format(key_plugin, status),sucess=True))
            else:
                print(display_messages('unknown plugin: {}'.format(key_plugin),error=True))
        except IndexError:
            print(display_messages('unknown sintax command',error=True))