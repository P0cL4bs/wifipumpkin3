from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.core.utility.printer import (
    setcolor,
    display_messages,
    display_tabulate,
)

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


class Ap(ExtensionUI):
    """ show all variable and status from AP """

    Name = "ap"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_ap", self.do_ap)
        self.register_command("help_ap", self.help_ap)

        super(Ap, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_ap(self):
        print(self.__doc__)

    def do_ap(self, args):
        """ap: show all variable and status from AP """
        headers_table, output_table = (
            ["BSSID", "SSID", "Channel", "Interface", "Status", "Security"],
            [],
        )
        print(display_messages("Settings AccessPoint:", info=True, sublime=True))
        status_ap = self.root.conf.get("accesspoint", "status_ap", format=bool)
        output_table.append(
            [
                self.root.conf.get("accesspoint", self.root.commands["bssid"]),
                self.root.conf.get("accesspoint", self.root.commands["ssid"]),
                self.root.conf.get("accesspoint", self.root.commands["channel"]),
                self.root.conf.get("accesspoint", self.root.commands["interface"]),
                setcolor("is Running", color="green")
                if status_ap
                else setcolor("not Running", color="red"),
                self.root.conf.get("accesspoint", self.root.commands["security"]),
            ]
        )
        display_tabulate(headers_table, output_table)
        enable_security = self.root.conf.get(
            "accesspoint", self.root.commands["security"], format=bool
        )

        if enable_security:
            headers_sec, output_sec = (
                ["wpa_algorithms", "wpa_sharedkey", "wpa_type"],
                [],
            )
            output_sec.append(
                [
                    self.root.conf.get("accesspoint", "wpa_algorithms"),
                    self.root.conf.get("accesspoint", "wpa_sharedkey"),
                    self.root.conf.get("accesspoint", "wpa_type"),
                ]
            )
            print(display_messages("Settings Security:", info=True, sublime=True))
            display_tabulate(headers_sec, output_sec)
            self.show_help_command("help_security_command")
