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


class Plugins(ExtensionUI):
    """ show all available plugins """

    Name = "plugins"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_plugins", self.do_plugins)
        self.register_command("help_plugins", self.help_plugins)

        super(Plugins, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_plugins(self):
        self.show_help_command("help_plugins_command")

    def do_plugins(self, args=str):
        """network: show all available plugins """
        headers_table, output_table = ["Name", "Active", "Description"], []
        headers_plugins, output_plugins = ["Name", "Active"], []
        all_plugins, config_instance = None, None
        for plugin_name, plugin_info in self.root.mitm_controller.getInfo().items():
            status_plugin = self.root.conf.get("mitm_modules", plugin_name, format=bool)
            output_table.append(
                [
                    plugin_name,
                    setcolor("True", color="green")
                    if status_plugin
                    else setcolor("False", color="red"),
                    plugin_info["Description"][:50] + "..."
                    if len(plugin_info["Description"]) > 50
                    else plugin_info["Description"],
                ]
            )
            if (
                self.root.mitm_controller.getInfo()[plugin_name]["Config"] != None
                and status_plugin
            ):
                config_instance = self.root.mitm_controller.getInfo()[plugin_name][
                    "Config"
                ]
                all_plugins = self.root.mitm_controller.getInfo()[plugin_name][
                    "Config"
                ].get_all_childname("plugins")

        print(display_messages("Available Plugins:", info=True, sublime=True))
        display_tabulate(headers_table, output_table)

        if not all_plugins:
            return

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
        print(display_messages("Sniffkin3 plugins:", info=True, sublime=True))
        return display_tabulate(headers_plugins, output_plugins)
