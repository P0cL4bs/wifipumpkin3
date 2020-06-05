import urwid, time, threading
from tabulate import tabulate
from netaddr import EUI
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
import fcntl, termios, struct, os
from wifipumpkin3.core.common.platforms import hexdump
from multiprocessing import Process
from wifipumpkin3.core.config.globalimport import *
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

palette_color = [
    ("titlebar", "", ""),
    ("refresh button", "dark green,bold", "black"),
    ("quit button", "dark red,bold", "black"),
    ("getting quote", "dark blue", "black"),
    ("getting quote", "dark blue", ""),
    ("headers", "black,bold", "black"),
    ("change", "dark green", ""),
    ("change negative", "dark red", ""),
    ("body", "white", "black"),
    ("title", "black", "dark blue"),
]


class ui_TableMonitorClient(WidgetBase):
    ConfigRoot = "ui_table_mod"
    SubConfig = "ui_table_mod"
    ID = "ui_table_mod"
    Name = "ui_table_mod"

    def __init__(self, parent):
        self.parent = parent
        self.table_clients = []
        self.__threadServices = []
        self.__threadStatus = False
        self.header_text = [
            ("titlebar", ""),
            "Clients: ",
            ("title", "UP"),
            ",",
            ("title", "DOWN"),
            ":scroll",
            "     Monitor DHCP Requests",
        ]

    def getClientsCount(self):
        return len(self.table_clients)

    def setup_view(self):
        self.header_wid = urwid.AttrWrap(urwid.Text(self.header_text), "title")
        self.menu = urwid.Text([u"Press (", ("quit button", u"Q"), u") to quit."])
        self.lwDevices = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.lwDevices)
        self.main_box = urwid.LineBox(self.body)

        self.layout = urwid.Frame(
            header=self.header_wid, body=self.main_box, footer=self.menu
        )
        self.add_Clients(Refactor.readFileDataToJson(C.CLIENTS_CONNECTED))

    def render_view(self):
        return self.layout

    def main(self):
        self.setup_view()
        loop = urwid.MainLoop(
            self.render_view(), palette=palette_color, unhandled_input=self.handleWindow
        )
        loop.set_alarm_in(1, self.refresh)
        loop.run()

    def refresh(self, loop=None, data=None):
        self.setup_view()
        loop.widget = self.render_view()
        loop.set_alarm_in(1, self.refresh)

    def start(self):
        self.main()

    def stop(self):
        if len(self.__threadServices) > 0:
            self.table_clients = []
            self.lwDevices.append(urwid.Text(("", self.up_Clients())))

    def get_mac_vendor(self, mac):
        """ discovery mac vendor by mac address """
        try:
            d_vendor = EUI(mac)
            d_vendor = d_vendor.oui.registration().org
        except:
            d_vendor = "unknown vendor"
        return d_vendor

    def add_Clients(self, data_dict):
        """ add client on table list() """
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
            self.lwDevices.clear()
            self.lwDevices.append(urwid.Text(("", self.up_Clients())))
            self._body.set_focus(len(self.lwDevices) - 1, "above")

    def up_Clients(self):
        if len(self.table_clients) > 0:
            return tabulate(self.table_clients, ("Hostname", "IP", "Mac", "Vendor"))
        return ""

    def handleWindow(self, key):
        if key == "R" or key == "r":
            pass
        elif key == "Q" or key == "q" or key == "esc":
            raise urwid.ExitMainLoop()
