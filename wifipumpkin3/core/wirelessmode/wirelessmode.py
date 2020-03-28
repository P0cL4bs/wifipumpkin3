from wifipumpkin3.core.config.globalimport import *
from re import *
from os import (
    system,path,getcwd,
    popen,listdir,mkdir,chown
)
from shutil import move
from wifipumpkin3.core.widgets.default.session_config import *


class Mode(Qt.QObject):
    configApMode = 'ap_mode'
    configRoot = "generic"
    SubConfig = "generic"
    ID = "GenericWirelessMode"
    Name = "Wireless Mode Generic"
    service = None
    reactor = None
    def __init__(self,parent=None,FSettings = None):
        super(Mode,self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()
        self.SettingsAP = {}
        
        #self.currentSessionID = self.parent.currentSessionID
        #self.SettingsAP = self.parent.SettingsAP
        #self.SessionsAP = self.parent.SessionsAP
        self.SessionConfig = SessionConfig.getInstance()
        self.interfacesLink = Refactor.get_interfaces()

    def checkifHostapdBinaryExist(self):
        """ check if hostapd binary file exist"""
        if path.isfile(self.hostapd_path):
            return True
        return False

    @property
    def getHostapdPath(self):
        return self.conf.get(self.configRoot, '{}_hostapd_path'.format(self.configRoot))

    def isChecked(self):
        return self.conf.get(self.configApMode, self.subConfig, format=bool)

    def get_soft_dependencies(self):
        ''' check if Hostapd, isc-dhcp-server is installed '''
        if not path.isfile(self.hostapd_path):
            return QtGui.QMessageBox.information(self,'Error Hostapd','hostapd is not installed')
        if self.FSettings.get_setting('accesspoint','dhcpd_server',format=bool):
            if not self.SettingsEnable['ProgCheck'][3]:
                return QtGui.QMessageBox.warning(self,'Error dhcpd','isc-dhcp-server (dhcpd) is not installed')
        return True

    def configure_network_AP(self):
        self.parent.configure_network_AP()
        
    def controlcheck(self,object):
        self.FSettings.set_setting('accesspoint',
                                            self.ID, self.controlui.isChecked())
        if self.Settings:
            self.Settings.setEnabled(self.controlui.isChecked())
            if self.controlui.isChecked():
                self.Settings.show()

            else:
                self.Settings.hide()

    @property
    def WirelessSettings(self):
        return self.SessionConfig.Wireless

    @property
    def Settings(self):
        pass

    def Initialize(self):
        pass

    def boot(self):
        pass

    def Shutdown(self):
        pass

    def Start(self):
        self.Initialize()
        self.boot()
        self.PostStart()

    def PostStart(self):
        #self.parent.set_status_label_AP(True)
        # TODO remove the code below as it has been replaced with proxy disables
        # self.ProxyPluginsTAB.GroupSettings.setEnabled(False)
        print('-------------------------------')
        # set configure iptables 
        self.setIptables()
        # print('AP::[{}] Running...'.format(self.WirelessSettings.EditSSID.text()))
        # print('AP::BSSID::[{}] CH {}'.format(Refactor.get_interface_mac(
        #     self.WirelessSettings.WLANCard.currentText()),
        #     self.WirelessSettings.EditChannel.value()))
        self.conf.set('accesspoint', 'statusAP', True)
        #self.conf.set('accesspoint', 'interfaceAP',str(self.WirelessSettings.WLANCard.currentText()))
        # check if Advanced mode is enable

    def setIptables(self):
        self.interfacesLink = Refactor.get_interfaces()
        print(display_messages('sharing internet connection with NAT...', info=True))
        self.ifaceHostapd = self.conf.get('accesspoint','interfaceAP')
        try:
            for ech in self.conf.get_all_childname('iptables'):
                ech = self.conf.get('iptables', ech)
                if '$inet' in ech and self.interfacesLink['activated'][0] != None:
                    ech = ech.replace('$inet',self.interfacesLink['activated'][0])
                if '$wlan' in ech:
                    ech = ech.replace('$wlan',self.ifaceHostapd)
                popen(ech)
        except Exception as e:
            print(e)

    def Stop(self):
        self.Shutdown()

    @property
    def DHCPClient(self):
        return DHCPClient.instances[0]

    def get_error_hostapdServices(self,data):
        '''check error hostapd on mount AP '''
        self.Shutdown()
        return QtGui.QMessageBox.warning(self,'[ERROR] Hostpad',
        'Failed to initiate Access Point, '
        'check output process hostapd.\n\nOutput::\n{}'.format(data))

    def LogOutput(self,data):
        ''' get inactivity client from hostapd response'''

        if self.DHCPClient.ClientTable.APclients != {}:
            if data in self.DHCPClient.ClientTable.APclients.keys():
                self.parent.StationMonitor.addRequests(data,self.DHCPClient.ClientTable.APclients[data],False)
            self.DHCPClient.ClientTable.delete_item(data)
            self.parent.connectedCount.setText(str(len(self.DHCPClient.ClientTable.APclients.keys())))





