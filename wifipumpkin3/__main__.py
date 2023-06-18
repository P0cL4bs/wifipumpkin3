# -*- coding: utf-8 -*-
from logging import getLogger, ERROR

from wifipumpkin3.core.config.setup import create_user_dir_config
getLogger("scapy.runtime").setLevel(ERROR)
import argparse
import sys
from PyQt5 import QtCore
from wifipumpkin3 import PumpkinShell
from wifipumpkin3.core.utility.printer import (
    banner,
    setcolor,
    display_messages,
    set_nocolors,
)
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3._version import __version__, __codename__, __branch__
from wifipumpkin3._author import __author__
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.common.platforms import Linux
from os import getuid
from wifipumpkin3.core.servers.rest.application import RestControllerAPI
import threading



def parser_args_func(parse_args, config):
    if parse_args.nocolors:
        set_nocolors()

    if parse_args.rm_networkmanager:
        if Linux.setNetworkManager(parse_args.rm_networkmanager, True):
            print(
                display_messages(
                    "The interface {} has been removed successfully\n".format(
                        setcolor(parse_args.rm_networkmanager, color="green")
                    ),
                    sucess=True,
                )
            )
            exit(0)
        print(
            display_messages(
                "The interface {} can't to ignore from Network-Manager\n".format(
                    setcolor(parse_args.rm_networkmanager, color="red")
                ),
                error=True,
            )
        )
        print(
            display_messages(
                "Please, check if you have Network-Manager installed",
                info=True,
            )
        )
        exit(1)
        
    if parse_args.ig_networkmanager:
        manager_ifaces = Linux.get_interfaces()
        if not parse_args.ig_networkmanager in manager_ifaces.get("all_wireless"):
            print(
                display_messages(
                    "{} invalid interface name\n The param -iNM require a valid interface wireless adapter.".format(
                        setcolor(parse_args.ig_networkmanager, color="red")
                    ),
                    error=True,
                )
            )
            exit(1)
        if Linux.setNetworkManager(parse_args.ig_networkmanager, False):
            print(
                display_messages(
                    "The interface {} has been ignored successfully".format(
                        setcolor(parse_args.ig_networkmanager, color="green")
                    ),
                    sucess=True,
                )
            )
            print(
                display_messages(
                    "For restore the interface use the param {} for remove card from network-manager".format(
                        setcolor("-rNM", color="yellow")
                    ),
                    info=True,
                )
            )
            exit(0)
        print(
            display_messages(
                "The interface {} can't to ignore from Network-Manager\n".format(
                    setcolor(parse_args.rm_networkmanager, color="red")
                ),
                error=True,
            )
        )
        print(
            display_messages(
                "Please, check if you have Network-Manager installed",
                info=True,
            )
        )
        exit(1)
    
    if parse_args.wireless_mode:
        if parse_args.wireless_mode in config.get_all_childname("ap_mode"):
            config.set_one("ap_mode", parse_args.wireless_mode, True)
            print(
                display_messages(
                    "Wireless Mode: {}".format(
                        setcolor(parse_args.wireless_mode, color="ciano")
                    ),
                    info=True,
                )
            )
    if parse_args.restmode:
        if not (parse_args.password):
            print(
                display_messages(
                    "{} \n rest mode require a valid password.".format(
                        setcolor("password invalid", color="red")
                    ),
                    info=True,
                )
            )
            exit(0)

        set_nocolors()
        config.set_one("ap_mode", "restapi", True)
        config.set("rest_api_settings", "PASSWORD", parse_args.password)
        config.set("rest_api_settings", "USERNAME", parse_args.username)
        config.set("rest_api_settings", "port", parse_args.restport)
        server_restapi = RestControllerAPI("wp3API", config)
        thead = threading.Thread(target=server_restapi.run)
        thead.setDaemon(True)
        thead.start()


def wp3_header():
    _author = "{}".format(setcolor(__author__, color="yellow"))
    _version = setcolor(__version__, color="yellow")
    _codename = setcolor(__codename__, color="ciano")
    _branch = setcolor(__branch__, color="purple")

    banner(_codename)
    print("by: {} - P0cL4bs Team | version: {} {}".format(_author, _version, _branch))


def main():

    app = QtCore.QCoreApplication(sys.argv)
    
    # create config dir if not have 
    create_user_dir_config()

    config = SettingsINI.getInstance()

    # settings default values that change on
    config.set("accesspoint", "status_ap", False)

    parser = argparse.ArgumentParser(
        description="wifipumpkin3 - Powerful framework for rogue access point attack."
    )
    parser.add_argument(
        "-i", dest="interface", help="set interface for create AP", default=""
    )
    parser.add_argument(
        "-iNet", dest="interface_net", required=False, help="set interface for share internet to AP", default=None
    )
    parser.add_argument(
        "-s", dest="session", help="set session for continue attack", default=None
    )
    parser.add_argument(
        "-p",
        "--pulp",
        dest="pulp",
        help="interactive sessions can be scripted with .pulp file",
        default="",
    )
    parser.add_argument(
        "-x",
        "--xpulp",
        dest="xpulp",
        help='interactive sessions can be string with ";" as the separator',
        default="",
    )
    parser.add_argument(
        "-m",
        "--wireless-mode",
        dest="wireless_mode",
        help="set wireless mode settings",
        default=None,
    )
    parser.add_argument(
        "--no-colors",
        dest="nocolors",
        help="disable terminal colors and effects.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--rest",
        dest="restmode",
        help="Run the Wp3 RESTful API.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--restport",
        dest="restport",
        help="Port to run the Wp3 RESTful API on. default is 1337",
        default=1337,
    )
    parser.add_argument(
        "--username",
        dest="username",
        help="Start the RESTful API with the specified username instead of pulling from wp3.db",
        default="wp3admin",
    )
    parser.add_argument(
        "--password",
        dest="password",
        help="Start the RESTful API with the specified password instead of pulling from wp3.db",
        default=None,
    )
    parser.add_argument(
        "-iNM",
        "--ignore-from-networkmanager",
        dest="ig_networkmanager",
        help="set interface for ignore from Network-Manager",
        default=None,
    )
    parser.add_argument(
        "-rNM",
        "--remove-from-networkmanager",
        dest="rm_networkmanager",
        help="remove interface from Network-Manager",
        default=None,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        dest="version",
        version="%(prog)s v{} branch: {}".format(__version__, __branch__),
    )

    parse_args = parser.parse_args()
    parser_args_func(parse_args, config)

    # check is rootuser
    if not getuid() == 0:
        sys.exit("[!] Wp3 must be run as root.")

    wp3_header()

    prompt = PumpkinShell(parse_args)
    prompt.cmdloop("Starting prompt...")
    sys.exit(app.exec_())
