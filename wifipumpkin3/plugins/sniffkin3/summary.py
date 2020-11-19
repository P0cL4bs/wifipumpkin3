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


class Summary(PSniffer):
    _activated = False
    _instance = None
    meta = {
        "Name": "summary",
        "Version": "1.0",
        "Description": "quick look at the packet is layers: ",
        "Author": "Pumpkin-Dev",
    }

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value

    @staticmethod
    def getInstance():
        if Summary._instance is None:
            Summary._instance = Summary()
        return Summary._instance

    def filterPackets(self, pkt):
        if (
            pkt.haslayer(Ether)
            and pkt.haslayer(Raw)
            and not pkt.haslayer(IP)
            and not pkt.haslayer(IPv6)
        ):
            return
        # if pkt.haslayer(DNSQR):
        #    print ('{} ->() has searched for: {}'.format(pkt[IP].src, pkt[DNS].qd.qname[:len(str(pkt[DNS].qd.qname)) - 1]))
        # return self.output.emit({'{}'.format(self.meta['Name']): "Packet : %s ==> %s" % (pkt[0][1].src, pkt[0][1].dst)})
