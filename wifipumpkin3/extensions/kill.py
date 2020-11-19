from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.core.utility.printer import setcolor, display_messages

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


class Kill(ExtensionUI):
    """ terminate a module in background by id """

    Name = "kill"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_kill", self.do_kill)
        self.register_command("help_kill", self.help_kill)
        self.register_command("complete_kill", self.complete_kill)

        super(Kill, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_kill(self):
        self.show_help_command("help_kill_command")

    def complete_kill(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.root.threads.get("Modules").keys())
                if command.startswith(text)
            ]
        else:
            return list(self.root.threads.get("Modules").keys())

    def do_kill(self, args):
        """core: terminate a module in background by id"""
        if len(self.root.threads["Modules"]) > 0:
            try:
                module_name = args.split()[0]
            except Exception:
                return
            module_instance = None
            if module_name in list(self.root.threads.get("Modules").keys()):
                module_instance = self.root.threads["Modules"].get(module_name)
            if not module_instance:
                print(
                    display_messages(
                        "the module {} was not found.".format(
                            setcolor(module_name, color="orange")
                        ),
                        error=True,
                    )
                )
                return
            return module_instance.do_stop([])
        print(
            display_messages(
                "there are no module running in the background", error=True
            )
        )
