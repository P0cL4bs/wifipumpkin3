from wifipumpkin3.core.common.terminal import ConsoleUI
from wifipumpkin3.core.controllers.defaultcontroller import *
from wifipumpkin3.core.config.globalimport import *

from wifipumpkin3.modules import *
from wifipumpkin3.modules import module_list

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

approot = QtCore.QCoreApplication.instance()


class PumpkinShell(Qt.QObject, ConsoleUI):
    """
    :parameters
        options : parse_args
    """

    instances = []
    _all_modules = None

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    @property
    def getDefault(self):
        """return DefaultWidget instance for load controllers"""
        return DefaultController.getInstance()

    def __init__(self, parse_args):
        self.__class__.instances.append(weakref.proxy(self))
        self.parse_args = parse_args
        # load session parser
        self.currentSessionID = self.parse_args.session
        if not self.currentSessionID:
            self.currentSessionID = Refactor.generate_session_id()
        print(
            display_messages(
                "Session id: {} ".format(
                    setcolor(self.currentSessionID, color="red", underline=True)
                ),
                info=True,
            )
        )

        super(PumpkinShell, self).__init__(parse_args=self.parse_args)

    def initialize_core(self):
        """this method is called in __init__"""
        # set current session unique id
        self.conf.set("accesspoint", "current_session", self.currentSessionID)
        # set interface for shared connection from params
        self.conf.set("accesspoint", "interface_net", self.parse_args.interface_net)
            
        if self.parse_args.interface:
            self.conf.set("accesspoint", "interface", self.parse_args.interface)

        self.all_modules = module_list

        # intialize the LoggerManager
        # TODO: this change solve IndexError: list index out of range
        # but not a definitive solution
        self.logger_manager = LoggerManager(self)
        self.coreui = DefaultController(self)

        # print(self.coreui.Plugins)
        self.proxy_controller = self.coreui.getController("proxy_controller")
        self.mitm_controller = self.coreui.getController("mitm_controller")
        self.wireless_controller = self.coreui.getController("wireless_controller")
        self.dhcp_controller = self.coreui.getController("dhcp_controller")
        self.dns_controller = self.coreui.getController("dns_controller")
        self.uiwid_controller = self.coreui.getController("ui_controller")

        self.parser_list_func = {
            # parser_set_proxy is default extend class
            "parser_set_proxy": self.proxy_controller.pumpkinproxy,
            "parser_set_plugin": self.mitm_controller.sniffkin3,
            "parser_set_mode": self.wireless_controller.Settings,
            "parser_set_security": self.wireless_controller.Settings,
            "parser_set_hostapd_config": self.wireless_controller.Settings,
            "parser_set_dhcpconf": self.wireless_controller.Settings,
            "parser_set_dhcpmode": self.dhcp_controller.Active,
        }
        self.parser_autcomplete_func = {}

        # hook function (plugins and proxies)
        self.intialize_hook_func(self.proxy_controller)
        self.intialize_hook_func(self.mitm_controller)

        # register autocomplete set security command
        self.parser_autcomplete_func[
            "parser_set_security"
        ] = self.wireless_controller.Settings.getCommandsSecurity
        self.parser_autcomplete_func[
            "parser_set_hostapd_config"
        ] = self.wireless_controller.Settings.getCommandsHostapd
        self.parser_autcomplete_func[
            "parser_set_dhcpconf"
        ] = self.wireless_controller.Settings.getCommandsDhcpConf
        self.parser_autcomplete_func[
            "parser_set_dhcpmode"
        ] = self.dns_controller.getCommandsDhcpMode

        self.commands = {
            "interface": "interface",
            "interface_net": "interface_net",
            "ssid": "ssid",
            "bssid": "bssid",
            "channel": "channel",
            "proxy": None,  # only for settings proxy
            "plugin": None,  # only for settings plugin
            "mode": None,  # only for settings mdoe
            "dhcpconf": None,  # only for settings dhcpconf
            "dhcpmode": None,  # only for settings dhcpmode
            "security": "enable_security",
            "hostapd_config": "enable_hostapd_config",
        }

        # get all command plugins and proxies
        for ctr_name, ctr_instance in self.coreui.getController(None).items():
            if hasattr(ctr_instance, "getInfo"):
                for plugin_name, plugins_info in ctr_instance.getInfo().items():
                    self.commands[plugin_name] = ""

        self.threads = {"RogueAP": [], "Modules": {}}

    @property
    def all_modules(self):
        return self._all_modules

    @all_modules.setter
    def all_modules(self, module_list):
        m_avaliable = {}
        for name, module in module_list().items():
            if hasattr(module, "ModPump"):
                m_avaliable[name] = module
        self._all_modules = m_avaliable

    def intialize_hook_func(self, controller):
        # load all parser funct and plguins command CLI for plugins
        for plugin_name in controller.getInfo():
            self.parser_list_func["parser_set_" + plugin_name] = getattr(
                controller, plugin_name
            )
            if getattr(controller, plugin_name).getPlugins != None:
                self.parser_autcomplete_func["parser_set_" + plugin_name] = getattr(
                    controller, plugin_name
                ).getPlugins

    def do_show(self, args):
        """core: show available modules"""
        headers_table, output_table = ["Name", "Description"], []
        print(display_messages("Available Modules:", info=True, sublime=True))
        for name, module in self.all_modules.items():
            output_table.append([name, getattr(module, "ModPump").__doc__])
        return display_tabulate(headers_table, output_table)

    def do_mode(self, args):
        """ap: all wireless mode available"""
        headers_table, output_table = ["ID", "Activate", "Description"], []
        print(display_messages("Available Wireless Mode:", info=True, sublime=True))
        for id_mode, info in self.wireless_controller.getInfo().items():
            output_table.append(
                [
                    id_mode,
                    setcolor("True", color="green")
                    if info["Checked"]
                    else setcolor("False", color="red"),
                    info["Name"],
                ]
            )
        return display_tabulate(headers_table, output_table)

    def do_use(self, args):
        """core: select module for modules"""
        if args in self.all_modules.keys():
            if module_list()[args].ModPump.getInstance() != None:
                module_list()[args].ModPump.getInstance().initialize()
                return (
                    module_list()[args]
                    .ModPump.getInstance()
                    .cmdloop(
                        "module: {} session has been restored".format(
                            setcolor(args, color="yellow")
                        )
                    )
                )
            module = module_list()[args].ModPump(self.parse_args, globals())
            module.initialize()
            return module.cmdloop()
        print(
            display_messages(
                "the module [{}] was not found or failed to import.".format(
                    setcolor(args, color="orange")
                ),
                error=True,
            )
        )

    def do_start(self, args):
        """ap: start access point service"""
        if len(self.threads["RogueAP"]) > 0:
            print(display_messages("the AP is running at full power.", error=True))
            return

        self.interfaces = Linux.get_interfaces()
        if not self.conf.get(
            "accesspoint", self.commands["interface"]
        ) in self.interfaces.get("all"):
            print(
                display_messages(
                    "the interface not found or is unavailable ", error=True
                )
            )
            sys.exit(1)

        if self.wireless_controller.Start() != None:
            return
        for ctr_name, ctr_instance in self.coreui.getController(None).items():
            if ctr_name != "wireless_controller":
                ctr_instance.Start()

        self.threads["RogueAP"].insert(0, self.dhcp_controller.ActiveReactor)
        self.threads["RogueAP"].insert(1, self.dns_controller.ActiveReactor)
        self.threads["RogueAP"].extend(self.proxy_controller.ActiveReactor)
        self.threads["RogueAP"].extend(self.mitm_controller.ActiveReactor)

        # self.wireless_controller.ActiveReactor.start()
        # self.wireless_controller.ActiveReactor.signalApIsRuning.connect(
        #     self.signalHostApdProcessIsRunning
        # )

        if not self.parse_args.restmode:
            self.wireless_controller.ActiveReactor.start()
            self.wireless_controller.ActiveReactor.signalApIsRuning.connect(
                self.signalHostApdProcessIsRunning
            )
            return

        self.wireless_controller.ActiveReactor.start()
        for thread in self.threads["RogueAP"]:
            if thread is not None:
                QtCore.QThread.sleep(1)
                if not (isinstance(thread, list)):
                    thread.start()

    def signalHostApdProcessIsRunning(self, status):
        if status:
            print(
                display_messages(
                    "hostapd is {}".format(setcolor("running", color="green")),
                    sucess=True,
                )
            )
            for thread in self.threads["RogueAP"]:
                if thread is not None:
                    QtCore.QThread.sleep(1)
                    if not (isinstance(thread, list)):
                        thread.start()
            self.threads["RogueAP"].insert(0, self.wireless_controller.ActiveReactor)

    def killThreads(self):

        # kill all modules on background
        if len(self.threads["Modules"]) > 0:
            for module_name, instance in self.threads.get("Modules").items():
                if instance._background_mode:
                    print(
                        display_messages(
                            "job {} successfully stopped".format(module_name),
                            sucess=True,
                        )
                    )
                    instance.do_stop([])

        if not len(self.threads["RogueAP"]) > 0:
            return
        self.conf.set("accesspoint", "status_ap", False)
        # get all command plugins and proxies
        try:
            for ctr_name, ctr_instance in self.coreui.getController(None).items():
                ctr_instance.Stop()

            for thread in self.threads["RogueAP"]:
                if thread is not None:
                    thread.stop()
        except Exception as e:
            pass

        for line in self.wireless_controller.Activated.getSettings().SettingsAP["kill"]:
            exec_bash(line)
        self.threads["RogueAP"] = []

    def do_ignore(self, args):
        """core: the message logger will be ignored"""
        logger = self.logger_manager.get(args)
        if logger != None:
            return logger.setIgnore(True)
        print(display_messages("Logger class not found.", error=True))

    def do_restore(self, args):
        """core: the message logger will be restored"""
        logger = self.logger_manager.get(args)
        if logger != None:
            return logger.setIgnore(False)
        print(display_messages("Logger class not found.", error=True))

    def do_stop(self, args):
        """ap: stop access point service"""
        self.killThreads()

    def do_jobs(self, args):
        """ap: show all threads/processes in background"""
        if len(self.threads["RogueAP"]) > 0:
            process_background = {}
            headers_table, output_table = ["ID", "PID"], []
            for ctr_name, ctr_instance in self.coreui.getController(None).items():
                if hasattr(ctr_instance, "getReactorInfo"):
                    process_background.update(ctr_instance.getReactorInfo())

            for id_controller, info in process_background.items():
                output_table.append([info["ID"], info["PID"]])

            print(display_messages("AP background:", info=True, sublime=True))
            return display_tabulate(headers_table, output_table)

        if len(self.threads["Modules"]) > 0:
            print(display_messages("Modules background:", info=True, sublime=True))
            headers_table, output_table = ["ID", "Status"], []
            for module_name, instance in self.threads.get("Modules").items():
                output_table.append(
                    [
                        module_name,
                        setcolor("is Running", color="green")
                        if instance._background_mode
                        else setcolor("not Running", color="red"),
                    ]
                )
            return display_tabulate(headers_table, output_table)

        print(
            display_messages("there are no tasks running in the background", error=True)
        )

    def do_set(self, args):
        """core: set variable proxy,plugin and access point"""
        try:
            command, value = args.split()[0], args.split()[1]
            if "bssid" in command:
                value = args[len("bssid ") :]
            elif "ssid" in command:
                value = args[len("ssid ") :]
        except IndexError:
            return print(
                display_messages("unknown sintax : {} ".format(args), error=True)
            )

        if command in list(self.commands.keys()) and self.commands[command]:
            # settings accesspoint if command is not None
            self.conf.set("accesspoint", self.commands[command], value)
            return

        for func in self.parser_list_func:
            if command in func or command.split(".")[0] in func:
                return getattr(self.parser_list_func[func], func)(value, args)

        # hook function configure plugin
        for plugin in self.parser_autcomplete_func:
            if command in self.parser_autcomplete_func[plugin]:
                return getattr(self.parser_list_func[plugin], plugin)(value, command)

        print(display_messages("unknown command: {} ".format(command), error=True))

    def do_unset(self, args):
        """core: unset variable commnd hostapd_config"""
        try:
            group_name, key = (
                args.split()[0].split(".")[0],
                args.split()[0].split(".")[1],
            )
            if key in self.conf.get_all_childname(group_name):
                return self.conf.unset(group_name, key)
            print(
                display_messages(
                    "unknown key : {} for hostapd_config".format(key), error=True
                )
            )
        except IndexError:
            return print(
                display_messages("unknown sintax : {} ".format(args), error=True)
            )

    def complete_ignore(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in self.logger_manager.all()
                if command.startswith(text)
            ]
        else:
            return list(self.logger_manager.all())

    def complete_restore(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in self.logger_manager.all()
                if command.startswith(text)
            ]
        else:
            return list(self.logger_manager.all())

    def complete_unset(self, text, args, start_index, end_index):
        if text:
            command_list = []
            for func in self.parser_autcomplete_func:
                if text.startswith(func.split("_set_")[1]):
                    for command in self.parser_autcomplete_func[func]:
                        if command.startswith(text):
                            command_list.append(command)
            return command_list
        else:
            return ["hostapd_config"]

    def complete_set(self, text, args, start_index, end_index):
        if text:
            command_list = []
            for func in self.parser_autcomplete_func:
                if text.startswith(func.split("_set_")[1]):
                    for command in self.parser_autcomplete_func[func]:
                        if command.startswith(text):
                            command_list.append(command)

            for command in self.commands:
                if command.startswith(text):
                    command_list.append(command)
            return command_list
        else:
            return list(self.commands.keys())

    def complete_use(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.all_modules.keys())
                if command.startswith(text)
            ]
        else:
            return list(self.all_modules.keys())

    def help_set(self):
        self.show_help_command("help_set_command")

    def help_unset(self):
        self.show_help_command("help_unset_command")

    def help_mode(self):
        self.show_help_command("help_mode_command")

    def do_exit(self, args):
        """core: exit program and all threads"""
        if len(self.threads["RogueAP"]) > 0:
            user_input = input("Do you really want to quit? [y/n]: ").lower()
            if user_input == 'y':
                self.killThreads()
        print("Exiting...")
        raise SystemExit
