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
    """Scan WiFi networks and detect devices"""

    name = "wifiscan"

    options = {
        "interface": ["wlanx", "Name network interface wireless "],
        "timeout": [0, "Time duration of scan network wireless (ex: 0 infinty)"],
    }
    completions = list(options.keys())

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        self.name_module = self.name
        self.whitelist = ["00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"]
        self.aps = {}
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

    def do_run(self, args):
        """execute module"""
        print(
            display_messages(
                "setting interface: {} monitor momde".format(
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
            try:
                essid = pkt[Dot11ProbeReq].info.decode('utf8')
            except UnicodeDecodeError:
                try:
                    essid = pkt[Dot11ProbeReq].info.decode('unicode-escape')
                except Exception:
                    try:
                        essid = pkt[Dot11ProbeReq].info.decode('latin1')
                    except Exception:
                        essid = "Not decoded ssid"
        else:
            essid = "Hidden SSID"
        client = pkt[Dot11].addr2

        if client in self.whitelist or essid in self.whitelist:
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
                    if not receiver in self.whitelist:
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
                    if not sender in self.whitelist:
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
            client in self.whitelist
            or essid in self.whitelist
            or bssid in self.whitelist
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

    def showDataOutputScan(self):
        os.system("clear")
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

        print(display_messages("press CTRL+C to stop scanning", info=True))

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

            self.showDataOutputScan()

    def set_monitor_mode(self, mode="manager"):
        if not self.options.get("interface")[0] in Linux.get_interfaces().get("all"):
            print(display_messages("the interface not found!", error=True))
            sys.exit(1)
        os.system("ifconfig {} down".format(self.options.get("interface")[0]))
        os.system("iwconfig {} mode {}".format(self.options.get("interface")[0], mode))
        os.system("ifconfig {} up".format(self.options.get("interface")[0]))
