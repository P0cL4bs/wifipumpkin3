from core.common.terminal import ModuleUI
from core.config.globalimport import *
from core.utility.printer import display_messages
from random import randrange
import time,signal,sys
from multiprocessing import Process
from scapy.all import *
from core.common.platforms import Linux
from tabulate import tabulate

class ModPump(ModuleUI):
    """ Scan WiFi networks and detect devices"""
    name = "wifi_scan"

    options = {
        "interface": "wlxc83a35cef744",
        "timeout": 10
    }
    completions = list(options.keys())

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        self.name_module = self.name
        self.set_prompt_modules()
        self.aps = {}
        self.table_headers = ["Channel","Privacy", "SSID" ,"BSSID"]
        self.table_output = []
        super(ModPump, self).__init__(parse_args=self.parse_args, root=self.root )

    def do_run(self, args):
        self.set_monitor_mode()

        self.p = Process(target = self.channel_hopper, args=(self.options.get("interface"),))
        self.p.start()

        sniff(iface=self.options.get("interface"), prn=self.sniffAp)
        

    def channel_hopper(self, interface):
        while True:
            try:
                channel = randrange(1,10)
                os.system("iw dev %s set channel %d" % (interface, channel))
                time.sleep(1)
            except KeyboardInterrupt:
                break

    def sniffAp(self, p):
        if ( (p.haslayer(Dot11Beacon))):
            ssid       = p[Dot11Elt].info
            bssid      = p[Dot11].addr3    
            channel    = int( ord(p[Dot11Elt:3].info))
            capability = p.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}\
                    {Dot11ProbeResp:%Dot11ProbeResp.cap%}")

            if (bssid in list(self.aps.keys())): return
                    
            if re.search("privacy", capability): enc = 'Y'
            else: enc  = 'N'

            self.aps[bssid] = {"ssid": ssid, "channel": channel, "capability": capability}
            self.table_output.append([int(channel), enc, ssid, bssid])
            os.system("clear")
            print(tabulate(self.table_output, self.table_headers, tablefmt="simple"))

    def set_monitor_mode(self):
        if not self.options.get("interface") in Linux.get_interfaces().get("all"):
            print(display_messages("the interface not found!", error=True))
            sys.exit(0)
        os.system("ifconfig {} down".format(self.options.get("interface")))
        os.system("iwconfig {} mode monitor".format(self.options.get("interface")))
        os.system("ifconfig {} up".format(self.options.get("interface")))