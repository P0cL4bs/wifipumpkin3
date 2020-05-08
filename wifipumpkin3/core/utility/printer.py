from tabulate import tabulate
from wifipumpkin3.core.utility.banners import random_banners

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


def set_nocolors():
    global colors
    colors = {
        "BOLD": "",
        "BLUE": "",
        "GREEN": "",
        "YELLOW": "",
        "RED": "",
        "ENDC": "",
        "CIANO": "",
        "ORAN_BG": "",
        "PUR_BG": "",
        "PUR": "",
        "ORAN": "",
        "GREY": "",
        "DARKGREY": "",
        "UNDERLINE": "",
    }


colors = {
    "BOLD": "\033[1m",
    "BLUE": "\033[34m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "CIANO": "\033[1;36m",
    "ORAN_BG": "\033[43m",
    "PUR_BG": "\033[45m",
    "PUR": "\033[35m",
    "ORAN": "\033[33m",
    "GREY": "\033[37m",
    "DARKGREY": "\033[1;30m",
    "UNDERLINE": "\033[4m",
}


def banner(name=""):
    print(random_banners().format(name))


def setcolor(text, color="", underline=False):
    strcolored = {
        "blue": "{}{}{}{}".format(colors["BOLD"], colors["BLUE"], text, colors["ENDC"]),
        "red": "{}{}{}{}".format(colors["BOLD"], colors["RED"], text, colors["ENDC"]),
        "ciano": "{}{}{}{}".format(
            colors["BOLD"], colors["CIANO"], text, colors["ENDC"]
        ),
        "green": "{}{}{}{}".format(
            colors["BOLD"], colors["GREEN"], text, colors["ENDC"]
        ),
        "purple": "{}{}{}{}".format(
            colors["BOLD"], colors["PUR"], text, colors["ENDC"]
        ),
        "orange": "{}{}{}{}".format(
            colors["BOLD"], colors["ORAN"], text, colors["ENDC"]
        ),
        "orange_bg": "{}{}{}{}".format(
            colors["BOLD"], colors["ORAN_BG"], text, colors["ENDC"]
        ),
        "purple_bg": "{}{}{}{}".format(
            colors["BOLD"], colors["PUR_BG"], text, colors["ENDC"]
        ),
        "yellow": "{}{}{}{}".format(
            colors["BOLD"], colors["YELLOW"], text, colors["ENDC"]
        ),
        "grey": "{}{}{}{}".format(colors["BOLD"], colors["GREY"], text, colors["ENDC"]),
        "darkgrey": "{}{}{}{}".format(
            colors["BOLD"], colors["DARKGREY"], text, colors["ENDC"]
        ),
    }
    if underline:
        return colors["UNDERLINE"] + strcolored[color]
    return strcolored[color]


def display_tabulate(header=[], content=[], tablefmt="presto", newline=True):
    print(tabulate(content, header, tablefmt=tablefmt))
    if newline:
        print("\n")


def display_messages(
    string,
    error=False,
    sucess=False,
    info=False,
    sublime=False,
    without=False,
    header=False,
):
    if sublime:
        if error:
            return "\n{}{}[-]{} {}\n===={}\n".format(
                colors["RED"], colors["BOLD"], colors["ENDC"], string, len(string) * "="
            )
        elif sucess:
            return "\n{}{}[+]{} {}\n===={}\n".format(
                colors["GREEN"],
                colors["BOLD"],
                colors["ENDC"],
                string,
                len(string) * "=",
            )
        elif info:
            return "\n{}{}[*]{} {}\n===={}\n".format(
                colors["BLUE"],
                colors["BOLD"],
                colors["ENDC"],
                string,
                len(string) * "=",
            )
        elif header:
            return "\n{}\n{}\n".format(string, len(string) * "=",)
    else:
        if error:
            return "{}{}[-]{} {}".format(
                colors["RED"], colors["BOLD"], colors["ENDC"], string
            )
        elif sucess:
            return "{}{}[+]{} {}".format(
                colors["GREEN"], colors["BOLD"], colors["ENDC"], string
            )
        elif info:
            return "{}{}[*]{} {}".format(
                colors["BLUE"], colors["BOLD"], colors["ENDC"], string
            )
