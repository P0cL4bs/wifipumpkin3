import urwid
from wifipumpkin3.core.ui.uimode import WidgetBase

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


class ui_DhcpSettingsClass(WidgetBase):
    ConfigRoot = "ui_dhcp_config"
    SubConfig = "ui_dhcp_config"
    ID = "ui_dhcp_config"
    Name = "ui_dhcp_config"

    def __init__(self, parent):
        self.parent = parent
        self.desc_dhcp_server = "DHCP or Dynamic Host Configuration Protocol is a protocol used in networks through which a system can automatically obtain the network settings, at boot time, required for communicating with other network devices. .\n"
        self.desc_ip_range = "Using DHCP, the Access Point will provide an IP address to devices that connect, in a private range.\n"
        self.class_headers = {
            "10.0.0.20/50": "Class-A-Address",
            "172.16.0.100/150": "Class-B-Address",
            "192.168.0.100/150": "Class-C-Address",
        }
        self.radio_dhcpd_server_status = False

    def setup_view(self):

        self.radio_dhcpd_server_status = self._conf.get(
            "accesspoint", "dhcpd_server", format=bool
        )

        self.widget_main = urwid.Padding(
            self.menu("DHCP Server", self.class_headers.keys()),
            left=2,
            right=2,
        )
        self.top = urwid.Overlay(
            self.widget_main,
            urwid.SolidFill("\N{MEDIUM SHADE}"),
            align="center",
            width=("relative", 60),
            valign="middle",
            height=("relative", 80),
            min_width=40,
            min_height=12,
        )

    def on_radioButton_changes(self, w, state, user_data):
        if "pydhcp_server" == user_data:
            self.radio_dhcpd_server_status = False
        else:
            self.radio_dhcpd_server_status = True

    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider(), urwid.Text(self.desc_dhcp_server)]

        bgroup = []  # button group
        self.radioPyDhcpServer = urwid.RadioButton(
            bgroup,
            "PyDHCPServer",
            state=not self.radio_dhcpd_server_status,
            on_state_change=self.on_radioButton_changes,
            user_data="pydhcp_server",
        )

        self.radioDhcpdServer = urwid.RadioButton(
            bgroup,
            "ISC DHCPServer",
            state=self.radio_dhcpd_server_status,
            on_state_change=self.on_radioButton_changes,
            user_data="dhcp_server",
        )

        body.append(self.radioPyDhcpServer)
        body.append(self.radioDhcpdServer)
        body.append(urwid.Divider())
        body.append(urwid.Text(self.desc_ip_range))

        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, "click", self.item_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map="reversed"))

        default_config = []
        child_keys = self._conf.get_all_childname("dhcp")
        for config in child_keys:
            default_config.append(
                "{} = {}\n".format(config, self._conf.get("dhcp", config))
            )

        body.append(urwid.Text(["\n[Default]\n"] + default_config))
        body.append(urwid.Text(["Press (", ("quit button", "Q"), ") to quit."]))

        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(self, button, choice):
        data_config = ["-----------DHCP-----------\n"]
        data_set = {}
        child_keys = self._conf.get_all_childname(self.class_headers.get(choice))
        for config in child_keys:
            data_config.append(
                "{} = {}\n".format(
                    config, self._conf.get(self.class_headers.get(choice), config)
                )
            )
            data_set[config] = self._conf.get(self.class_headers.get(choice), config)
        data_config.append("-----------DHCP-----------\n")

        for key, value in data_set.items():
            self._conf.set("dhcp", key, value)

        if self.radioDhcpdServer.get_state():
            self._conf.set("accesspoint", "pydhcp_server", False)
            self._conf.set("accesspoint", "pydns_server", False)
            self._conf.set("accesspoint", "dhcpd_server", True)
        else:
            self._conf.set("accesspoint", "pydhcp_server", True)
            self._conf.set("accesspoint", "pydns_server", True)
            self._conf.set("accesspoint", "dhcpd_server", False)

        response = urwid.Text(["[DHCP configuration]", "\n"] + data_config)
        done = urwid.Button("Ok")
        urwid.connect_signal(done, "click", self.exit_program)
        self.widget_main.original_widget = urwid.Filler(
            urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")])
        )

    def render_view(self):
        return self.layout

    def main(self):
        self.setup_view()
        urwid.MainLoop(
            self.top,
            palette=[("reversed", "standout", "")],
            unhandled_input=self.handleWindow,
        ).run()

    def start(self):
        self.main()

    def handleWindow(self, key):
        if key == "Q" or key == "q" or key == "esc":
            raise urwid.ExitMainLoop()

    def exit_program(self, button):
        raise urwid.ExitMainLoop()
