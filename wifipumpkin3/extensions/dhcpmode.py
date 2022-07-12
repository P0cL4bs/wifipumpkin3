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


class DhcpMode(ExtensionUI):
    """show/set all available dhcp server"""

    Name = "dhcpmode"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_dhcpmode", self.do_dhcpmode)
        self.register_command("help_dhcpmode", self.help_dhcpmode)
        self.register_command("complete_dhcpmode", self.complete_dhcpmode)

        super(DhcpMode, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_dhcpmode(self):
        print(
            display_messages(
                "use the command `{} dhcp_id` for change the default dhcp implementation.".format(
                    setcolor("dhcpmode", color="orange")
                ),
                info=True,
            )
        )
        print(
            display_messages(
                "use the command `set {}.[variable] [value]` for set options DNS.".format(
                    setcolor("dhcpmode", color="orange")
                ),
                info=True,
            )
        )
        print(display_messages("Info: ", info=True, sublime=True))
        print(
            display_messages(
                "dhcpd_server : use the ISC DHCP for configure the dns/dhcp server.",
                info=True,
            )
        )
        print(
            display_messages(
                "pydhcp_server : use the python implementation for configure the dns/dhcp server.",
                info=True,
            )
        )
        print("\n")

    def complete_dhcpmode(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.root.dhcp_controller.getInfo().keys())
                if command.startswith(text)
            ]
        else:
            return list(self.root.dhcp_controller.getInfo().keys())

    def do_dhcpmode(self, args):
        """ap: show/set all available dhcp server"""

        headers_table, output_table = (
            ["ID", "Status", "Description"],
            [],
        )
        print(display_messages("DHCP Server:", info=True, sublime=True))
        for key, instance in self.root.dhcp_controller.getInfo().items():
            output_table.append(
                [
                    key,
                    setcolor("True", color="green")
                    if instance.isChecked()
                    else setcolor("False", color="red"),
                    instance.Name,
                ]
            )
        display_tabulate(headers_table, output_table)

        if self.conf.get("accesspoint", "pydns_server", format=bool):
            print(display_messages("Settings DNS:", info=True, sublime=True))
            options = [
                key for key in self.conf.get_all_childname("accesspoint") 
                if str(key).startswith('pydns')
            ] 
            for config in options:
                print(
                    " {}={}".format(
                        setcolor(config, color="purple"), 
                        self.conf.get("accesspoint", config)
                    )
                )
            print('\n')
