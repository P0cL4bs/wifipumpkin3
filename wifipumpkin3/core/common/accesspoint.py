import configparser
from grp import getgrnam
from os import popen, path, mkdir, chown
from pwd import getpwnam
from shutil import move
from subprocess import \
    (check_output,
     STDOUT, CalledProcessError,
     Popen, PIPE, call
     )

from PyQt5.QtCore import pyqtSignal,QObject
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.common.platforms import Linux
from wifipumpkin3.core.common.platforms import exec_bash
from wifipumpkin3.core.controls.threads import ProcessHostapd
from wifipumpkin3.core.packets.dhcpserver import DHCPThread
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.utility.printer import display_messages
import time


class AccessPoint(Linux):
    sendStatusPoint = pyqtSignal(bool)
    sendStatusIface = pyqtSignal(bool)
    def __init__(self,parent):
        super(AccessPoint, self)
        QObject.__init__(self)
        self.parent         = parent
        self.conf           = SettingsINI(C.CONFIG_INI)
        self.ifaceHostapd   = self.conf.get('accesspoint','interfaceAP')
        self.threadsAP      = {'RougeAP': []}
        self.DHCP           = self.getDHCPConfig()
        self.queue          = []

    def Configure(self):
        ''' configure interface and dhcpd for mount Access Point '''
        self.SettingsAP = {
        'interface':
            [
                'ifconfig %s up'%(self.ifaceHostapd),
                'ifconfig %s %s netmask %s'%(self.ifaceHostapd,self.DHCP['router'],self.DHCP['netmask']),
                'ifconfig %s mtu 1400'%(self.ifaceHostapd),
                'route add -net %s netmask %s gw %s'%(self.DHCP['subnet'],
                self.DHCP['netmask'],self.DHCP['router'])
            ],
        'kill':
            [
                'iptables -w --flush',
                'iptables -w --table nat --flush',
                'iptables -w --delete-chain',
                'iptables -w --table nat --delete-chain',
                'killall dhpcd 2>/dev/null',
                'ifconfig {} down'.format(self.ifaceHostapd),
                'ifconfig {} up'.format(self.ifaceHostapd),
                'ifconfig {} 0'.format(self.ifaceHostapd),
            ],
        'hostapd':
            [
                'interface={}\n'.format(self.ifaceHostapd),
                'ssid={}\n'.format(self.conf.get('accesspoint','ssid')),
                'channel={}\n'.format(self.conf.get('accesspoint','channel')),
                'bssid={}\n'.format(self.conf.get('accesspoint','bssid')),
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
                'option domain-name \"%s\";\n'%(self.conf.get('accesspoint','ssid')),
                'option domain-name-servers {};\n'.format('8.8.8.8'),
                'range {};\n'.format(self.DHCP['range'].replace('/',' ')),
                '}',
            ],
        }
        print(display_messages('enable forwarding in iptables...',sucess=True))
        Linux.set_ip_forward(1)
        # clean iptables settings
        for line in self.SettingsAP['kill']: exec_bash(line)
        # set interface using ifconfig
        for line in self.SettingsAP['interface']: exec_bash(line)
        # check if dhcp option is enabled.
        if self.conf.get('accesspoint','dhcp_server',format=bool):
            with open(C.DHCPCONF_PATH,'w') as dhcp:
                for line in self.SettingsAP['dhcp-server']: dhcp.write(line)
                dhcp.close()
                if not path.isdir('/etc/dhcp/'): mkdir('/etc/dhcp')
                move(C.DHCPCONF_PATH, '/etc/dhcp/')


    def checkNetworkAP(self):
        # check if interface has been support AP mode (necessary for hostapd)
        if self.conf.get('accesspoint','check_support_ap_mode',format=bool):
            if not 'AP' in self.get_supported_interface(self.ifaceHostapd)['Supported']:
                print(display_messages('No Network Supported failed',error=True))
                print('failed AP ode: warning interface, the feature\n'
                'Access Point Mode is Not Supported By This Device ->({}).\n'
                'Your adapter does not support for create Access Point Network.\n'.format(self.ifaceHostapd))
                return False

        # check if Wireless interface is being used
        if self.ifaceHostapd == self.interfaces['activated'][0]:
            iwconfig = Popen(['iwconfig'], stdout=PIPE,shell=False,stderr=PIPE)
            for line in iwconfig.stdout.readlines():
                if self.ifaceHostapd in str(line,encoding='ascii'):
                    print(display_messages('Wireless interface is busy',error=True))
                    print('Connection has been detected, this {} is joined the correct Wi-Fi network\n'
                    'Device or resource busy\n{}\nYou may need to another Wi-Fi USB Adapter\n'
                    'for create AP or try use with local connetion(Ethernet).\n'
                    ''.format(self.ifaceHostapd,str(line,encoding='ascii')))
                    return False

        # check if range ip class is same
        gateway_wp, gateway = self.DHCP['router'],self.interfaces['gateway']
        if gateway != None:
            if gateway_wp[:len(gateway_wp)-len(gateway_wp.split('.').pop())] == \
                gateway[:len(gateway)-len(gateway.split('.').pop())]:
                print(display_messages('DHCP Server settings',error=True))
                print('The DHCP server check if range ip class is same.\n'
                    'it works, but not share internet connection in some case.\n'
                    'for fix this, You need change on tab (settings -> Class Ranges)\n'
                    'now you have choose the Class range different of your network.\n')
                return False
        return True

    def check_Wireless_Security(self):
        pass

    def start(self):
        # check connection with internet
        self.interfaces = Linux.get_interfaces()
        if not (self.checkNetworkAP()):
            return

        # check if using ethernet or wireless connection
        print(display_messages('configuring hostapd...',info=True))
        if self.interfaces['activated'][1] == 'ethernet' or self.interfaces['activated'][1] == 'ppp' \
                or self.interfaces['activated'][0] == None: #allow use without internet connection
            # change Wi-Fi state card
            Linux.kill_procInterfaceBusy() # killing network process
            try:
                check_output(['nmcli','radio','wifi',"off"]) # old version
            except Exception:
                try:
                    check_output(['nmcli','nm','wifi',"off"]) # new version
                except Exception as error:
                    print(display_messages('Error nmcli',error=True))
                    print(error)
            finally:
                call(['rfkill', 'unblock' ,'wifi'])

        #configure interface
        self.Configure()
        self.check_Wireless_Security() # check if user set wireless password

        ignore = ('interface=','ssid=','channel=','essid=')
        with open(C.HOSTAPDCONF_PATH,'w') as apconf:
            for i in self.SettingsAP['hostapd']:apconf.write(i)
            apconf.close()

        # create thread for hostapd and connect get_Hostapd_Response function
        self.hostapd_path = self.conf.get('accesspoint', 'hostapd_path')
        #self.Thread_hostapd = ProcessHostapd([self.hostapd_path,C.HOSTAPDCONF_PATH], 'MDSNjD')
        self.Thread_hostapd = ProcessHostapd({self.hostapd_path :[C.HOSTAPDCONF_PATH]}, 'MDSNjD')
        self.Thread_hostapd.setObjectName('hostapd')
        self.Thread_hostapd.statusAP_connected.connect(self.get_Hostapd_Response)
        self.Thread_hostapd.statusAPError.connect(self.get_error_hostapdServices)
        self.threadsAP['RougeAP'].append(self.Thread_hostapd)

        # create thread dhcpd and connect fuction get_DHCP_Requests_clients
        print(display_messages('configuring dhcpd...',info=True))
        if  self.conf.get('accesspoint','dhcpd_server',format=bool):
            # create dhcpd.leases and set permission for acesss DHCPD
            leases = C.DHCPLEASES_PATH
            if not path.exists(leases[:-12]):
                mkdir(leases[:-12])
            if not path.isfile(leases):
                with open(leases, 'wb') as leaconf:
                    leaconf.close()
            uid = getpwnam('root').pw_uid
            gid = getgrnam('root').gr_gid
            chown(leases, uid, gid)

        elif self.conf.get('accesspoint','pydhcp_server',format=bool):
            if self.conf.get('accesspoint','pydns_server',format=bool):
                pass

        self.threadDHCP = DHCPThread(self.ifaceHostapd,self.DHCP)
        self.threadsAP['RougeAP'].append(self.threadDHCP)
        self.threadDHCP.DHCPProtocol._request.connect(self.get_DHCPoutPut)

        print(display_messages('sharing internet connection with NAT...', info=True))
        try:
            for ech in self.conf.get_all_childname('iptables'):
                ech = self.conf.get('iptables', ech)
                if '$inet' in ech:
                    ech = ech.replace('$inet',self.interfaces['activated'][0])
                if '$wlan' in ech:
                    ech = ech.replace('$wlan',self.ifaceHostapd)
                popen(ech)
        except: pass

        for thread in self.threadsAP['RougeAP']:
            time.sleep(3)
            thread.start()

        # save settings AP
        self.conf.set('accesspoint','statusAP',True)
        self.conf.set('accesspoint','interfaceAP',self.ifaceHostapd)
        self.sendStatusPoint.emit(True)

    def stop(self):
        if not len(self.threadsAP['RougeAP']) > 0:
            return
        self.conf.set('accesspoint', 'statusAP',False)
        for thread in self.threadsAP['RougeAP']:
            thread.stop()

        if hasattr(self,'SettingsAP'):
            for line in self.SettingsAP['kill']: exec_bash(line)
        self.threadsAP['RougeAP'] = []

    def get_DHCPoutPut(self, data):
        self.parent.ui_table.add_Clients(data)
        print(data)

    def get_PumpkinProxy_output(self, data):
        print(data)

    def get_Hostapd_Response(self,data):
        print(data)

    def get_error_hostapdServices(self,data):
        if  self.conf.get('accesspoint','statusAP',format=bool):
            print(display_messages('Hostapd Error',error=True))
            print(data)

    def getDHCPConfig(self):
        DHCP ={}
        DHCP['leasetimeDef'] = self.conf.get('dhcpdefault','leasetimeDef')
        DHCP['leasetimeMax'] = self.conf.get('dhcpdefault','leasetimeMax')
        DHCP['subnet'] = self.conf.get('dhcpdefault','subnet')
        DHCP['router'] = self.conf.get('dhcpdefault','router')
        DHCP['netmask'] = self.conf.get('dhcpdefault','netmask')
        DHCP['broadcast'] = self.conf.get('dhcpdefault','broadcast')
        DHCP['range'] = self.conf.get('dhcpdefault','range')
        return DHCP


    def get_supported_interface(self,dev):
        ''' get all support mode from interface wireless  '''
        _iface = {'info':{},'Supported': []}
        try:
            output = check_output(['iw',dev,'info'],stderr=STDOUT, universal_newlines=True)
            for line in output.split('\n\t'):
                _iface['info'][line.split()[0]] = line.split()[1]
            rulesfilter = '| grep "Supported interface modes" -A 10 | grep "*"'
            supportMode = popen('iw phy{} info {}'.format(_iface['info']['wiphy'],rulesfilter)).read()
            for mode in supportMode.split('\n\t\t'):
                _iface['Supported'].append(mode.split('* ')[1])
        except CalledProcessError:
            return _iface
        return _iface

    def setNetworkManager(self, interface=str,Remove=False):
        ''' mac address of interface to exclude '''
        networkmanager = C.NETWORKMANAGER
        config  = configparser.RawConfigParser()
        MAC     = Linux.get_interface_mac(interface)
        exclude = {'MAC': 'mac:{}'.format(MAC),'interface': 'interface-name:{}'.format(interface)}
        if  not Remove:
            if path.exists(networkmanager):
                config.read(networkmanager)
                try:
                    config.add_section('keyfile')
                except configparser.DuplicateSectionError:
                    config.set('keyfile','unmanaged-devices','{}'.format(
                        exclude['interface'] if MAC != None else exclude['MAC']))
                else:
                    config.set('keyfile','unmanaged-devices','{}'.format(
                        exclude['interface'] if MAC != None else exclude['MAC']))
                finally:
                    with open(networkmanager, 'wb') as configfile:
                        config.write(configfile)
                return True
            return False
        elif Remove:
            if path.exists(networkmanager):
                config.read(networkmanager)
                try:
                    config.remove_option('keyfile','unmanaged-devices')
                    with open(networkmanager, 'wb') as configfile:
                        config.write(configfile)
                        return True
                except configparser.NoSectionError:
                    return True
            return False