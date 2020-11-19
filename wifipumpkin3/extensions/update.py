from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.printer import display_messages, setcolor
from scapy.all import *
from wifipumpkin3.core.common.platforms import is_tool
import re

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


class Update(ExtensionUI):
    """ pulling updates from remote git repository """

    Name = "update"

    options = {
        "branches": ["dev", "beta", "master", "news", "test"],
        "default_branch": ["dev", "Name of current github branch"],
        "urlparser": "pip3 install --upgrade git+git://github.com/P0cL4bs/wifipumpkin3@{}",
    }
    completions = options.get("branches")

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_update", self.do_update)
        self.register_command("complete_update", self.complete_update)
        self.register_command("help_update", self.help_update)

        super(Update, self).__init__(parse_args=self.parse_args, root=self.root)

    def check_deps_pip(self):
        return is_tool("pip3")

    def help_update(self):
        print(
            "\n".join(
                [
                    " Usage: update [branch]",
                    " param branch: default is dev,options: master, ",
                    " news, test and beta. \n",
                    " Description:",
                    "  pulling updates from remote git repository",
                    "",
                ]
            )
        )

    def complete_update(self, text, args, start_index, end_index):
        if text:
            return [command for command in self.completions if command.startswith(text)]
        else:
            return self.completions

    def do_update(self, args):
        """core: pulling updates from remote git repository """
        if not self.check_deps_pip():
            print(display_messages("pip3: command not found", error=True))
            print(
                display_messages(
                    "Pip3 is not installed, check that you’ve installed all the necessary prerequisite packages, which include python3-dev, libffi-dev, and libssl-dev.",
                    info=True,
                )
            )
            return

        branch = None
        if args:
            branch = args.split()[0]
            if not branch in self.options.get("branches"):
                print(
                    display_messages(
                        "branch: {} not found! ".format(setcolor(branch, color="red")),
                        info=True,
                    )
                )
                return

        if not branch:
            branch = self.options.get("default_branch")[0]

        print(display_messages("pulling updates from remote git repository", info=True))
        print(
            display_messages(
                "from branch: {}".format(setcolor(branch, color="green")), info=True,
            )
        )

        anwer_question = input("So, do you want to continue to update ? (Y/N): ")
        if anwer_question.lower() != "y":
            return

        os.system(self.options.get("urlparser").format(branch))
        self.root.do_exit([])
