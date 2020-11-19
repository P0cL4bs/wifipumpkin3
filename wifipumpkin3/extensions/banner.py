from wifipumpkin3.core.common.terminal import ExtensionUI
from wifipumpkin3._version import __version__, __codename__, __branch__
from wifipumpkin3._author import __author__
from wifipumpkin3.core.utility.printer import banner, setcolor, display_messages

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


class Banner(ExtensionUI):
    """ display an awesome wp3 banner """

    Name = "banner"

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root

        self.register_command("do_banner", self.do_banner)
        self.register_command("help_banner", self.help_banner)

        super(Banner, self).__init__(parse_args=self.parse_args, root=self.root)

    def help_banner(self):
        print(self.__doc__)

    def do_banner(self, args):
        """core: display an awesome wp3 banner """
        _author = "{}".format(setcolor(__author__, color="yellow"))
        _version = setcolor(__version__, color="yellow")
        _codename = setcolor(__codename__, color="ciano")
        _branch = setcolor(__branch__, color="purple")

        banner(_codename)
        print(
            "by: {} - P0cL4bs Team | version: {} {}".format(_author, _version, _branch)
        )
        print(
            display_messages(
                "Session id: {} ".format(
                    setcolor(self.root.currentSessionID, color="red", underline=True)
                ),
                info=True,
            )
        )
