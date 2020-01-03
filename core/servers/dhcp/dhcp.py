from re import *
from netaddr import EUI
from core.config.globalimport import *
from core.common.uimodel import *
from core.utility.component import ControllerBlueprint
from isc_dhcp_leases.iscdhcpleases import IscDhcpLeases
from core.controls.threads import ProcessThread


class DHCPServers(QtCore.QObject,ComponentBlueprint):
    Name = "Generic"
    ID = "Generic"
    haspref = False
    ExecutableFile=""
    def __init__(self,parent=0):
        super(DHCPServers,self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()

        self.DHCPConf = self.Settings.confingDHCP

    # def controlcheck(self,object):
    #     self.FSettings.Settings.set_setting('dhcpserver', self.ID, self.controlui.isChecked())
    
    def prereq(self):
        pass
        # dh, gateway = self.DHCPConf['router'], Linux.get_interfaces()
        # # dh, gateway = self.PumpSettingsTAB.getPumpkinSettings()['router'],str(self.EditGateway.text())
        # if dh[:len(dh) - len(dh.split('.').pop())] == gateway[:len(gateway) - len(gateway.split('.').pop())]:
        #     print(display_messages('DHCP Server settings',
        #                                      'The DHCP server check if range ip class is same.'
        #                                      'it works, but not share internet connection in some case.\n'
        #                                      'for fix this, You need change on tab (settings -> Class Ranges)'
        #                                      'now you have choose the Class range different of your network.',error=True))


    def isChecked(self):
        return self.conf.get('accesspoint', self.ID, format=bool)

    def Stop(self):
        self.shutdown()
        self.reactor.stop()

    def Start(self):
        self.prereq()
        self.Initialize()
        self.boot()

    @property
    def Settings(self):
        return DHCPSettings.instances[0]

    @property
    def commandargs(self):
        pass

    def boot(self):
        print(self.command,self.commandargs)
        self.reactor = ProcessThread({self.command: self.commandargs})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.Name)  # use dns2proxy as DNS server

    @property
    def command(self):
        cmdpath = os.popen('which {}'.format(self.ExecutableFile)).read().split('\n')[0]
        if cmdpath:
            return cmdpath
        else:
            return None

    def get_mac_vendor(self,mac):
        ''' discovery mac vendor by mac address '''
        try:
            d_vendor = EUI(mac)
            d_vendor = d_vendor.oui.registration().org
        except:
            d_vendor = 'unknown mac'
        return d_vendor

    # def add_data_into_QTableWidget(self,client):
    #     self.HomeDisplay.ClientTable.addNextWidget(client)

    # def add_DHCP_Requests_clients(self,mac,user_info):
    #     self.parent.StationMonitor.addRequests(mac,user_info,True)

    # def get_DHCP_Discover_clients(self,message):
    #     '''get infor client connected with AP '''
    #     self.APclients = {}
    #     if message['mac_addr'] not in self.HomeDisplay.ClientTable.APclients.keys():
    #         self.APclients[message['mac_addr']] = \
    #         {'IP': message['ip_addr'],
    #         'device': message['host_name'],
    #          'MAC': message['mac_addr'],
    #          'Vendors' : self.get_mac_vendor(message['mac_addr'])}

    #         self.add_DHCP_Requests_clients(message['mac_addr'],self.APclients[message['mac_addr']])
    #         self.add_data_into_QTableWidget(self.APclients)
    #         self.parent.connectedCount.setText(str(len(self.HomeDisplay.ClientTable.APclients.keys())))

    # def get_DHCP_Requests_clients(self,data):
    #     ''' filter: data info sended DHCPD request '''
    #     self.APclients = {}
    #     if len(data) == 8:
    #         device = sub(r'[)|(]',r'',data[5])
    #         if len(device) == 0: device = 'unknown'
    #         if Refactor.check_is_mac(data[4]):
    #             if data[4] not in self.HomeDisplay.APclients.keys():
    #                 self.APclients[data[4]] = {'IP': data[2],
    #                 'device': device,'MAC': data[4],'Vendors' : self.get_mac_vendor(data[4])}
    #                 self.add_DHCP_Requests_clients(data[4],self.APclients[data[4]])
    #     elif len(data) == 9:
    #         device = sub(r'[)|(]',r'',data[6])
    #         if len(device) == 0: device = 'unknown'
    #         if Refactor.check_is_mac(data[5]):
    #             if data[5] not in self.HomeDisplay.ClientTable.APclients.keys():
    #                 self.APclients[data[5]] = {'IP': data[2],
    #                 'device': device,'MAC': data[5],'Vendors' : self.get_mac_vendor(data[5])}
    #                 self.add_DHCP_Requests_clients(data[5],self.APclients[data[5]])
    #     elif len(data) == 7:
    #         if Refactor.check_is_mac(data[4]):
    #             if data[4] not in self.HomeDisplay.ClientTable.APclients.keys():
    #                 leases = IscDhcpLeases(C.DHCPLEASES_PATH)
    #                 hostname = None
    #                 try:
    #                     for item in leases.get():
    #                         if item.ethernet == data[4]:
    #                             hostname = item.hostname
    #                     if hostname == None:
    #                         item = leases.get_current()
    #                         hostname = item[data[4]]
    #                 except:
    #                     hostname = 'unknown'
    #                 if hostname == None or len(hostname) == 0:hostname = 'unknown'
    #                 self.APclients[data[4]] = {'IP': data[2],'device': hostname,
    #                                            'MAC': data[4], 'Vendors': self.get_mac_vendor(data[4])}
    #                 self.add_DHCP_Requests_clients(data[4],self.APclients[data[4]])
    #     if self.APclients != {}:
    #         self.add_data_into_QTableWidget(self.APclients)
    #         self.parent.connectedCount.setText(str(len(self.HomeDisplay.ClientTable.APclients.keys())))



class DHCPSettings(CoreSettings):
    Name = "WP DHCP"
    ID = "DHCP"
    ConfigRoot = "dhcpdefault"
    Category = "DHCP"
    instances=[]
    confingDHCP={}

    def __init__(self,parent=0):
        super(DHCPSettings,self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__

        self.dhmode = [mod(parent) for mod in DHCPServers.__subclasses__()]
        self.updateconf()

    def updateconf(self):
        self.confingDHCP['leasetimeDef'] = self.conf.get(self.ConfigRoot,'leasetimeDef')
        self.confingDHCP['leasetimeMax'] = self.conf.get(self.ConfigRoot,'leasetimeMax')
        self.confingDHCP['subnet'] = self.conf.get(self.ConfigRoot,'subnet')  
        self.confingDHCP['router'] =  self.conf.get(self.ConfigRoot,'router')
        self.confingDHCP['netmask'] =  self.conf.get(self.ConfigRoot,'netmask')
        self.confingDHCP['broadcast'] = self.conf.get(self.ConfigRoot,'broadcast')
        self.confingDHCP['range'] = self.conf.get(self.ConfigRoot,'range')