from core.servers.mitm.mitmmode import MitmMode
from core.common.uimodel import *
from core.config.globalimport import *
from core.widgets.docks.dock import DockableWidget


class NetCredential(DockableWidget):
    id = "NetCredential"
    title = "Net Crendential"
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

class NetCreds(MitmMode):
    #TODO: implement a module example to mitmmode
    Name = "Net Credentials"
    ID = "NetCreds"
    Author = "PumpkinDev"
    Description = "Sniff passwords and hashes from an interface or pcap file coded by: Dan McInerney"
    LogFile = C.LOG_CREDSCAPTURE
    _cmd_array = []
    ModSettings = True
    ModType = "proxy"  # proxy or server
    def __init__(self,parent,FSettingsUI=None,main_method=None,  **kwargs):
        super(NetCreds, self).__init__(parent)
        self.setID(self.ID)
        self.setModType(self.ModType)
        self.dockwidget = NetCredential(None,title=self.Name)

    @property
    def CMD_ARRAY(self):
        self._cmd_array=['ping','google.com']
        return self._cmd_array


