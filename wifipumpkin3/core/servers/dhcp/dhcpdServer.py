from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.servers.dhcp.dhcp import DHCPServers
from wifipumpkin3.core.utility.printer import display_messages, setcolor
from wifipumpkin3.core.common.threads import ProcessThread
from os import path, mkdir, chown
from pwd import getpwnam
from grp import getgrnam
from re import sub
from isc_dhcp_leases.iscdhcpleases import IscDhcpLeases


class DhcpdServer(DHCPServers):
    Name = "Dhcpd DHCP Server"
    ID = "dhcpd_server"
    LogFile = C.LOG_PYDHCPSERVER
    ExecutableFile = "dhcpd"

    def __init__(self, parent=0):
        super(DhcpdServer, self).__init__(parent)
        self._isRunning = False
        self.leases = {}

    def setIsRunning(self, value):
        self._isRunning = value

    @property
    def getStatusReactor(self):
        return self._isRunning
    
    def Initialize(self):
        self.ifaceHostapd = self.conf.get("accesspoint", "interface")
        leases = C.DHCPLEASES_PATH
        if not path.exists(leases[:-12]):
            mkdir(leases[:-12])
        if not path.isfile(leases):
            with open(leases, "wb") as leaconf:
                leaconf.close()
        uid = getpwnam("root").pw_uid
        gid = getgrnam("root").gr_gid
        chown(leases, uid, gid)

    def boot(self):
        self.reactor = ProcessThread({self.command: self.commandargs})
        self.reactor._ProcssOutput.connect(self.logOutputDhcpServer)
        self.reactor.setObjectName(self.Name)

    def add_DHCP_Requests_clients(self, mac, user_info):
        # self.parent.StationMonitor.addRequests(mac,user_info,True)
        self.logger.info(
            "{} on {} join the AP".format(user_info["IP"], user_info["MAC"])
        )
        self.logger.info(
            "DHCP: {} to {} hostname:[{}] vendor:[{}]".format(
                user_info["MAC"],
                user_info["IP"],
                user_info["HOSTNAME"],
                user_info["VENDOR"],
            )
        )
        print(
            display_messages(
                "{} client join the AP".format(
                    setcolor(mac, color="green")
                ),
                info=True,
            )
        )
        self._connected[mac] = user_info

    def logOutputDhcpServer(self, data):
        """filter: data info sended DHCPD request"""
        raw_data = data
        data = data.split()
        if self.conf.get("accesspoint", "status_ap", format=bool):
            if len(data) == 8:
                device = sub(r"[)|(]", r"", data[5])
                if len(device) == 0:
                    device = "unknown"
                if Refactor.check_is_mac(data[4]):
                    if data[4] not in self.leases.keys():
                        self.leases[data[4]] = {
                            "IP": data[2],
                            "HOSTNAME": device,
                            "MAC": data[4],
                            "VENDOR": self.get_mac_vendor(data[4]),
                        }
                        self.add_DHCP_Requests_clients(data[4], self.leases[data[4]])
            elif len(data) == 9:
                device = sub(r"[)|(]", r"", data[6])
                if len(device) == 0:
                    device = "unknown"
                if Refactor.check_is_mac(data[5]):
                    if data[5] not in self.leases.keys():
                        self.leases[data[5]] = {
                            "IP": data[2],
                            "HOSTNAME": device,
                            "MAC": data[5],
                            "VENDOR": self.get_mac_vendor(data[5]),
                        }
                        self.add_DHCP_Requests_clients(data[5], self.leases[data[5]])
            elif len(data) == 7:
                if Refactor.check_is_mac(data[4]):
                    if data[4] not in self.leases.keys():
                        leases = IscDhcpLeases(C.DHCPLEASES_PATH)
                        hostname = None
                        try:
                            for item in leases.get():
                                if item.ethernet == data[4]:
                                    hostname = item.hostname
                            if hostname == None:
                                item = leases.get_current()
                                hostname = item[data[4]]
                        except:
                            hostname = "unknown"
                        if hostname == None or len(hostname) == 0:
                            hostname = "unknown"
                        self.leases[data[4]] = {
                            "IP": data[2],
                            "HOSTNAME": hostname,
                            "MAC": data[4],
                            "VENDOR": self.get_mac_vendor(data[4]),
                        }
                        self.add_DHCP_Requests_clients(data[4], self.leases[data[4]])

            self.logger.info(raw_data)

    @property
    def commandargs(self):
        return [
            "-d",
            "-f",
            "-lf",
            C.DHCPLEASES_PATH,
            "-cf",
            "/etc/dhcp/dhcpd.conf",
            self.ifaceHostapd,
        ]
