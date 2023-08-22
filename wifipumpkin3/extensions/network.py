from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.core.utility.printer import setcolor, display_messages
from wifipumpkin3.core.config.globalimport import *

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2023 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Network(ExtensionUI):
    """show informations about connections"""

    Name = "network"

    def __init__(self, parse_args=None, root = None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_network", self.do_network)

        super(Network, self).__init__(parse_args=self.parse_args, root=self.root)

    def do_network(self, args):
        """core: show informations about connections"""
        print(
            display_messages(
                "Default Connection Information", info=True, sublime=True
            )
        )
        self.interfacesLink = Refactor.get_interfaces()
        default_iface = self.interfacesLink["activated"][0]
        print(display_messages("Interface: {} Type: {}".format(setcolor(default_iface, color="yellow"), setcolor(self.interfacesLink["activated"][1], color="yellow")),info=True))
        print(display_messages("Internet status: {}".format(
            setcolor("On", color="green") if 
            Refactor.checkInternetConnectionFromInterface(default_iface) else
            setcolor("Off", color="red")), info=True))
        
        print(
            display_messages(
                "Wireless Network Information", info=True, sublime=True
            )
        )
        wireless_ifaces = self.interfacesLink["all_wireless"]
        for iface in wireless_ifaces:
            support_modes = Refactor.get_supported_interface(iface)["Supported"]
            print(display_messages("Interface: {} | AP mode support::[{}]".format(
                setcolor(iface, color="yellow"),
                setcolor("true", color="green") if "AP" in support_modes else setcolor("false", color="red")
            ), info=True))