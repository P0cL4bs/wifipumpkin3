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


class Proxies(ExtensionUI):
    """ show all available proxies """

    Name = "proxies"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_proxies", self.do_proxies)
        self.register_command("help_proxies", self.help_proxies)

        super(Proxies, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_proxies(self):
        self.show_help_command("help_proxies_command")

    def do_proxies(self, args):
        """network: show all available proxies"""
        headers_table, output_table = ["Proxy", "Active", "Port", "Description"], []
        plugin_info_activated = None
        config_instance = None
        headers_plugins, output_plugins = ["Name", "Active"], []

        for plugin_name, plugin_info in self.root.proxy_controller.getInfo().items():
            status_plugin = self.root.conf.get(
                "proxy_plugins", plugin_name, format=bool
            )
            # save plugin activated infor
            if plugin_info["Config"] != None:
                if (
                    self.root.conf.get_name_activated_plugin("proxy_plugins")
                    == plugin_name
                ):
                    plugin_info_activated = plugin_info
                    config_instance = plugin_info_activated["Config"]

            output_table.append(
                [
                    plugin_name,
                    setcolor("True", color="green")
                    if status_plugin
                    else setcolor("False", color="red"),
                    plugin_info["Port"],
                    plugin_info["Description"][:50] + "..."
                    if len(plugin_info["Description"]) > 50
                    else plugin_info["Description"],
                ]
            )

        print(display_messages("Available proxies:", info=True, sublime=True))
        display_tabulate(headers_table, output_table)
        # check plugin none
        if not plugin_info_activated:
            return
        # check if plugin selected is iquals the plugin config
        if plugin_info_activated["ID"] != self.root.conf.get_name_activated_plugin(
            "proxy_plugins"
        ):
            return
        all_plugins = plugin_info_activated["Config"].get_all_childname("plugins")
        for plugin_name in all_plugins:
            status_plugin = config_instance.get("plugins", plugin_name, format=bool)
            output_plugins.append(
                [
                    plugin_name,
                    setcolor("True", color="green")
                    if status_plugin
                    else setcolor("False", color="red"),
                ]
            )
        print(
            display_messages(
                "{} plugins:".format(plugin_info_activated["Name"]),
                info=True,
                sublime=True,
            )
        )
        return display_tabulate(headers_plugins, output_plugins)
