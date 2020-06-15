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


class Info(ExtensionUI):
    """ get information about proxy/plugin settings """

    Name = "info"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_info", self.do_info)
        self.register_command("help_info", self.help_info)
        self.register_command("complete_info", self.complete_info)

        super(Info, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_info(self):
        self.show_help_command("help_info_command")

    def complete_info(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.root.commands.keys())
                if command.startswith(text)
            ]
        else:
            return list(self.root.commands.keys())

    def do_info(self, args):
        """core: get information about proxy/plugin settings"""
        try:
            command = args.split()[0]
            plugins = self.root.mitm_controller.getInfo().get(command)
            proxies = self.root.proxy_controller.getInfo().get(command)
            if plugins or proxies:
                print(
                    display_messages(
                        "Information {}: ".format(command), info=True, sublime=True
                    )
                )
            if plugins:
                for name, info in plugins.items():
                    if name != "Config":
                        print(
                            " {} : {}".format(
                                setcolor(name, color="blue"),
                                setcolor(info, color="yellow"),
                            )
                        )
            if proxies:
                for name, info in proxies.items():
                    if name != "Config":
                        print(
                            " {} : {}".format(
                                setcolor(name, color="blue"),
                                setcolor(info, color="yellow"),
                            )
                        )
                try:
                    commands = proxies["Config"].get_all_childname("plugins")
                    list_commands = []
                    headers_table, output_table = ["Plugin", "Value"], []
                    # search plugin of proxy has string "set_"

                    for command in commands:
                        for sub_plugin in proxies["Config"].get_all_childname(
                            "set_{}".format(command)
                        ):
                            output_table.append(
                                [
                                    setcolor(
                                        "{}.{}".format(command, sub_plugin),
                                        color="blue",
                                    ),
                                    proxies["Config"].get(
                                        "set_{}".format(command), sub_plugin
                                    ),
                                ]
                            )
                    if output_table != []:
                        print(display_messages("Plugins:", info=True, sublime=True))
                        display_tabulate(headers_table, output_table)

                    settings = proxies["Config"].get_all_childname("settings")
                    if not settings:
                        return
                    headers_settings, output_settings = ["Setting", "Value"], []
                    # search extra settings plugin

                    for command in settings:
                        output_settings.append(
                            [
                                setcolor("{}".format(command), color="blue",),
                                proxies["Config"].get("settings", command),
                            ]
                        )
                    if output_settings != []:
                        print(display_messages("Settings:", info=True, sublime=True))
                        return display_tabulate(headers_settings, output_settings)

                except AttributeError:
                    pass

            if plugins or proxies:
                print("\n")
                return
        except IndexError:
            pass
        print(
            display_messages(
                "the parameter {} was not found.".format(
                    setcolor(args, color="orange")
                ),
                error=True,
            )
        )
