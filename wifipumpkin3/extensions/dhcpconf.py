from ast import arg
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


class Dhcpconf(ExtensionUI):
    """show/choise dhcp server configuration"""

    Name = "dhcpconf"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_dhcpconf", self.do_dhcpconf)
        self.register_command("help_dhcpconf", self.help_dhcpconf)
        self.ip_class = ["Class-A-Address", "Class-B-Address", "Class-C-Address"]
        super(Dhcpconf, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_dhcpconf(self):
        self.show_help_command("help_dhcpconf_command")

    def do_dhcpconf(self, args):
        """ap: show/choise dhcp server configuration"""
        status_ap = self.root.conf.get("accesspoint", "status_ap", format=bool)
        if args:
            try:
                id_dhcp_option = int(args.split()[0])
                selected_id_option = self.ip_class[id_dhcp_option]
                for key in self.root.conf.get_all_childname(selected_id_option):
                    self.root.conf.set(
                        "dhcp", key, self.root.conf.get(selected_id_option, key)
                    )

                if status_ap:
                    print(
                        display_messages(
                            "OBS: this settings require restart the AP", error=True
                        )
                    )

                return
            except Exception:
                return print(
                    display_messages(
                        "the parameter id {} was not found.".format(
                            setcolor(args, color="orange")
                        ),
                        error=True,
                    )
                )
        headers_table, output_table = (
            ["Id", "Class", "IP address range", "Netmask", "Router"],
            [],
        )
        print(display_messages("DHCP Server Option:", info=True, sublime=True))
        for ip_class in self.ip_class:
            output_table.append(
                [
                    self.ip_class.index(ip_class),
                    ip_class.split("-")[1],
                    self.root.conf.get(ip_class, "range"),
                    self.root.conf.get(ip_class, "netmask"),
                    self.root.conf.get(ip_class, "router"),
                ]
            )
        display_tabulate(headers_table, output_table, tablefmt="presto", newline=False)
        print(display_messages("DHCP Server Settings:", info=True, sublime=True))
        for config in self.root.conf.get_all_childname("dhcp"):
            print(
                " {}={}".format(
                    setcolor(config, color="purple"), self.root.conf.get("dhcp", config)
                )
            )
        print("\n")
