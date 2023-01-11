from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.core.servers.dhcp.dhcp import DHCPServers
from wifipumpkin3.core.utility.printer import (
    display_messages,
    display_tabulate,
)
from wifipumpkin3.core.lib.mac_vendor_lookup import MacLookup, BaseMacLookup, VendorNotFoundError
import wifipumpkin3.core.utility.constants as C

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


class Clients(ExtensionUI):
    """show all connected clients on AP"""

    Name = "clients"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_clients", self.do_clients)

        super(Clients, self).__init__(parse_args=self.parse_args, root=self.root)

    def get_mac_vendor(self, mac):
        """discovery mac vendor by mac address"""
        BaseMacLookup.cache_path = "{}/config/mac-vendors.txt".format(C.user_config_dir)
        mac_obj = MacLookup()
        try:
            d_vendor = mac_obj.lookup(mac)
        except VendorNotFoundError:
            return "unknown vendor"
        return d_vendor 

    def do_clients(self, args):
        """ap: show all connected clients on AP"""
        dhcp_mode: DHCPServers = self.root.getDefault.getController("dhcp_controller").Active
        data_dict: dict = dhcp_mode.getStaClients
        if not data_dict:
            print(display_messages("No clients connected on AP!", error=True))
            return
        self.table_clients = []
        for data in data_dict:
            self.table_clients.append(
                [
                    data_dict[data]["HOSTNAME"],
                    data_dict[data]["IP"],
                    data_dict[data]["MAC"],
                    self.get_mac_vendor(data_dict[data]["MAC"]),
                ]
            )
        print(display_messages("Clients:", info=True, sublime=True))
        display_tabulate(("Hostname", "IP", "Mac", "Vendor"), self.table_clients)
        print(display_messages("Total Devices: {}\n".format(len(data_dict)), info=True))