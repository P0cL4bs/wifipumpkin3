from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.printer import display_messages, setcolor
from scapy.all import *
import re

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


class Dump(ExtensionUI):
    """ get informations from clients connected on AccessPoint"""

    Name = "dump"

    options = {
        "interface": ["None", "Name network interface wireless "],
        "target": [
            "ff:ff:ff:ff:ff:ff",
            "the device MAC Address from client connected on AP,the default is for all clients",
        ],
    }
    completions = list(options.keys())

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_dump", self.do_dump)
        self.register_command("complete_dump", self.complete_dump)
        self.register_command("help_dump", self.help_dump)

        super(Dump, self).__init__(parse_args=self.parse_args, root=self.root)

    def getDataFromOutput(self, output):
        p = re.compile(r"\s+(.*):\s+(.*)")
        macaddr = self.getMacAddressFromData(output)
        data = {macaddr: {}}
        all_items = re.findall(p, output)
        for item in all_items:
            data[macaddr][item[0]] = item[1]
        return data

    def getMacAddressFromData(self, output):
        p = re.compile(r"([0-9a-f]{2}(?::[0-9a-f]{2}){5})", re.IGNORECASE)
        return re.findall(p, output)[0]

    def showResultData(self, data):
        try:
            rdata = self.getDataFromOutput(data)
        except IndexError:
            print(display_messages("cannot tracked: client not found.", error=True))
            return
        mac_addr = list(rdata.keys())[0]
        print(
            display_messages(
                "peer: [{}]".format(setcolor(mac_addr, color="green")), info=True
            )
        )
        for item in rdata:
            for key, value in rdata[item].items():
                print(
                    "     {} : {}".format(
                        setcolor(key, color="blue"), setcolor(value, color="yellow")
                    )
                )
        if rdata:
            print("\n")

    def help_dump(self):
        print(
            "\n".join(
                [
                    " Usage: dump [mac_address]",
                    " param mac_address: get info specific client (optional)\n",
                    " Description:",
                    "  Return information from clients like Signal, Connected time, Rx bytes, Authenticated and more ",
                    "",
                ]
            )
        )

    def complete_dump(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.root.all_modules.keys())
                if command.startswith(text)
            ]
        else:
            return list(self.root.all_modules.keys())

    def do_dump(self, args):
        """ap: dump informations from client connected on AP """
        self.options["target"][0] = None
        if len(args.split()) > 0:
            mac_addr = args.split()[0]
            if Refactor.check_is_mac(mac_addr):
                self.options["target"][0] = mac_addr
            if not self.options.get("target")[0]:
                print(
                    display_messages(
                        "the MAC: {} address format is invalid.".format(mac_addr),
                        error=True,
                    )
                )
                return
            self.targets = [self.options.get("target")[0]]
        else:
            self.targets = list(Refactor.readFileDataToJson(C.CLIENTS_CONNECTED).keys())

        self.output_commands = {}
        self.iface = self.conf.get("accesspoint", "interface")
        self.args_template = "iw dev {} station get {}"

        for mac in self.targets:
            self.output_commands[mac] = os.popen(
                self.args_template.format(self.iface, mac)
            ).read()

        for mac in self.output_commands:
            self.showResultData(self.output_commands.get(mac))
