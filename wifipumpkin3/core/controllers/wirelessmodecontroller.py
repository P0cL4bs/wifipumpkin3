from wifipumpkin3.core.config.globalimport import *
from os import (
    system,path,getcwd,
    popen,listdir,mkdir,chown
)
from shutil import move
from pwd import getpwnam
from grp import getgrnam
from wifipumpkin3.core.wirelessmode import *
from json import dumps,loads
#from core.widgets.default.SessionConfig import *
from datetime import datetime
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.wirelessmode import *

class WirelessModeController(object):

    def __init__(self, parent, **kwargs):
        super(WirelessModeController,self).__init__()
        self.parent = parent
        #self.setHidden(True) # hide widget on home
        self.conf = SettingsINI.getInstance()
        #self.SessionsAP = loads(str(self.FSettings.Settings.get_setting('accesspoint', 'sessions')))
        #self.currentSessionID = self.parent.currentSessionID
        #self.SettingsAP = self.parent.SettingsAP
        #self.SessionConfig = SessionConfig.instances[0]

    @property
    def Activated(self):
        return self.Settings.getActiveMode

    @property
    def getAllModeInfo(self):
        return self.Settings.getModesInfo

    @property
    def ActiveReactor(self):
        return self.Settings.getActiveMode.reactor

    @property
    def Settings(self):
        return AccessPointSettings.instances[0]

    def Start(self):
        ''' start Access Point and settings plugins  '''
        # if len(self.Settings.WLANCard.currentText()) == 0:
        #     return QtGui.QMessageBox.warning(self, 'Error interface ', 'Network interface is not found')
        # if not type(self.Activated.get_soft_dependencies()) is bool: return

        # # check if interface has been support AP mode (necessary for hostapd)
        # if self.FSettings.Settings.get_setting('accesspoint', 'check_support_ap_mode', format=bool):
        #     if not 'AP' in Refactor.get_supported_interface(self.Settings.WLANCard.currentText())['Supported']:
        #         return QtGui.QMessageBox.warning(self, 'No Network Supported failed',
        #                                          "<strong>failed AP mode: warning interface </strong>, the feature "
        #                                          "Access Point Mode is Not Supported By This Device -><strong>({})</strong>.<br><br>"
        #                                          "Your adapter does not support for create Access Point Network."
        #                                          " ".format(self.Settings.WLANCard.currentText()))

        # # check connection with internet
        # #self.interfacesLink = Refactor.get_interfaces()
        # # check if Wireless interface is being used
        # if str(self.Settings.WLANCard.currentText()) == self.Activated.interfacesLink['activated'][0]:
        #     iwconfig = Popen(['iwconfig'], stdout=PIPE, shell=False, stderr=PIPE)
        #     for line in iwconfig.stdout.readlines():
        #         if str(self.Settings.WLANCard.currentText()) in line:
        #             return QtGui.QMessageBox.warning(self, 'Wireless interface is busy',
        #                                              'Connection has been detected, this {} is joined the correct Wi-Fi network'
        #                                              ' : Device or resource busy\n{}\nYou may need to another Wi-Fi USB Adapter'
        #                                              ' for create AP or try use with local connetion(Ethernet).'.format(
        #                                                  str(self.Settings.WLANCard.currentText()), line))
        # # check if using ethernet or wireless connection
        # print('[*] Configuring {}...'.format(self.Activated.Name))
        # self.parent.SettingsEnable['AP_iface'] = str(self.Settings.WLANCard.currentText())
        # set_monitor_mode(self.parent.SettingsEnable['AP_iface']).setDisable()
        # if self.Activated.interfacesLink['activated'][1] == 'ethernet' or self.Activated.interfacesLink['activated'][1] == 'ppp' \
        #         or self.Activated.interfacesLink['activated'][0] == None:  # allow use without internet connection
        #     # change Wi-Fi state card
        #     Refactor.kill_procInterfaceBusy()  # killing network process
        #     try:
        #         check_output(['nmcli', 'radio', 'wifi', "off"])  # old version
        #     except Exception:
        #         try:
        #             check_output(['nmcli', 'nm', 'wifi', "off"])  # new version
        #         except Exception as error:
        #             return QtGui.QMessageBox.warning(self, 'Error nmcli', str(error))
        #     finally:
        #         call(['rfkill', 'unblock', 'wifi'])

        self.Activated.Start()
        #self.Settings.setEnabled(False)
        return None


    def Stop(self):
        pass
        #self.Settings.setEnabled(True)





class AccessPointSettings(CoreSettings):
    Name = "Access Point"
    ID = "Wireless"
    Category = "Wireless"
    instances=[]
    def __init__(self,parent):
        super(AccessPointSettings,self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__

        self.__modelist = [mode(self.parent) for mode in wirelessmode.Mode.__subclasses__()]
        
    def ModelistChanged(self,mode,widget):
        pass

    @property
    def getActiveMode(self):
        for mode in self.__modelist:
            if mode.isChecked():
                return mode
    
    @property
    def getModesInfo(self):
        mode_info = {}
        for mode in self.__modelist:
            mode_info[mode.ID] = {
                'Name' : mode.Name,
                'Checked' : mode.isChecked(),
                'ID': mode.ID}  
        return mode_info 
    
    @property
    def getInstances(self):
        return self.instances


    def parser_set_mode(self, mode_name, *args):
        # default parser mode commands complete
        if mode_name in self.conf.get_all_childname('ap_mode'):
            mode_selected =self.conf.get_name_activated_plugin('ap_mode')
            if (mode_selected != None):
                self.conf.set('ap_mode', mode_name, True)
                for mode in self.conf.get_all_childname('ap_mode'):
                    if mode != mode_name:
                        self.conf.set('ap_mode', mode, False)
                return
        return print(display_messages('unknown command: {} '.format(mode_name),error=True))

   
    def configure_network_AP(self):
        ''' configure interface and dhcpd for mount Access Point '''
        self.DHCP = self.Settings.DHCP.conf
        self.SettingsEnable['PortRedirect'] = self.settings.get_setting('settings','redirect_port')
        self.SettingsAP = {
        'interface':
            [
                'ifconfig %s up'%(self.SettingsEnable['AP_iface']),
                'ifconfig %s %s netmask %s'%(self.SettingsEnable['AP_iface'],self.DHCP['router'],self.DHCP['netmask']),
                'ifconfig %s mtu 1400'%(self.SettingsEnable['AP_iface']),
                'route add -net %s netmask %s gw %s'%(self.DHCP['subnet'],
                self.DHCP['netmask'],self.DHCP['router'])
            ],
        'kill':
            [
                'iptables --flush',
                'iptables --table nat --flush',
                'iptables --delete-chain',
                'iptables --table nat --delete-chain',
                'ifconfig %s 0'%(self.SettingsEnable['AP_iface']),
                'killall dhpcd 2>/dev/null',
            ],
        'hostapd':
            [
                'interface={}\n'.format(str(self.Settings.WLANCard.currentText())),
                'ssid={}\n'.format(str(self.EditApName.text())),
                'channel={}\n'.format(str(self.EditChannel.value())),
                'bssid={}\n'.format(str(self.EditBSSID.text())),
            ],
        'dhcp-server':
            [
                'authoritative;\n',
                'default-lease-time {};\n'.format(self.DHCP['leasetimeDef']),
                'max-lease-time {};\n'.format(self.DHCP['leasetimeMax']),
                'subnet %s netmask %s {\n'%(self.DHCP['subnet'],self.DHCP['netmask']),
                'option routers {};\n'.format(self.DHCP['router']),
                'option subnet-mask {};\n'.format(self.DHCP['netmask']),
                'option broadcast-address {};\n'.format(self.DHCP['broadcast']),
                'option domain-name \"%s\";\n'%(str(self.EditApName.text())),
                'option domain-name-servers {};\n'.format('8.8.8.8'),
                'range {};\n'.format(self.DHCP['range'].replace('/',' ')),
                '}',
            ],
        }
        print('[*] Enable forwarding in iptables...')
        Refactor.set_ip_forward(1)
        # clean iptables settings
        for line in self.SettingsAP['kill']: exec_bash(line)
        # set interface using ifconfig
        for line in self.SettingsAP['interface']: exec_bash(line)
        # check if dhcp option is enabled.
        if self.FSettings.Settings.get_setting('accesspoint','dhcp_server',format=bool):
            with open(C.DHCPCONF_PATH,'w') as dhcp:
                for line in self.SettingsAP['dhcp-server']:dhcp.write(line)
                dhcp.close()
                if not path.isdir('/etc/dhcp/'): mkdir('/etc/dhcp')
                move(C.DHCPCONF_PATH, '/etc/dhcp/')



        