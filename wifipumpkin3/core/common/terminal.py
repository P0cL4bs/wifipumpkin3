from cmd import Cmd
from wifipumpkin3.core.utility.printer import *
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
from os import popen, path
import sys
from wifipumpkin3.core.common.platforms import Linux
import weakref

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


class ConsoleUI(Cmd):
    """ shell console UI """

    def __init__(self, parse_args=None):
        self.parse_args = parse_args
        Cmd.__init__(self)
        self.conf = SettingsINI.getInstance()
        self.set_prompt()
        self.initialize_core()
        self.setOptions()

    def cmdloop(self, intro=None):
        print(intro)
        doQuit = False
        while doQuit != True:
            try:
                super(ConsoleUI, self).cmdloop(intro="")
                doQuit = True
            except KeyboardInterrupt:
                print("caught ctrl+c, press return to exit")
                self.do_exit([])

    def initialize_core(self):
        raise NotImplementedError()

    def setOptions(self):
        if self.parse_args.pulp:
            self.loadPulpFiles(self.parse_args.pulp)
        elif self.parse_args.xpulp:
            self.onecmd(self.parse_args.xpulp, ";")

    def set_prompt(self):
        self.prompt = "{} > ".format(setcolor("wp3", color="blue", underline=True))

    def do_search(self, args):
        """core: search modules by name"""
        pass

    def do_use(self, args):
        """core: load module on session"""
        pass

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        Cmd.preloop(self)  ## sets up command completion
        self._hist = []  ## No history yet
        self._locals = {}  ## Initialize execution namespace for user
        self._globals = {}

    def do_help(self, args):
        """core: show this help """
        if args:
            try:
                func = getattr(self, "help_" + args)
            except AttributeError:
                try:
                    head, doc = str(getattr(self, "do_" + args).__doc__).split(":")
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (args,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            names.sort()
            categorys = {
                "core": {"Core Commands": []},
                "ap": {"Ap Commands": []},
                "network": {"Network Commands": []},
            }
            print(display_messages("Available Commands:", sublime=True, info=True))

            for name in names:
                if name[:3] == "do_":
                    pname = name
                    cmd = name[3:]
                    if getattr(self, name).__doc__:
                        head, doc = str(getattr(self, name).__doc__).split(":")
                        if head in categorys:
                            categorys[head][list(categorys[head].keys())[0]].append(
                                (cmd, doc)
                            )

            for item in categorys:
                print(
                    display_messages(
                        "{}:".format(list(categorys[item].keys())[0]),
                        sublime=True,
                        header=True,
                    )
                )
                print("    {}	 {}".format("Command", "Description"))
                print("    {}	 {}".format("-------", "-----------"))
                for command, doc in categorys[item][list(categorys[item].keys())[0]]:
                    print("    {:<10}	{}".format(command, doc))
            print("\n")

    def default(self, args=str):
        for goodArgs in C.SYSTEMCOMMAND:
            if args.startswith(goodArgs):
                output = popen(args).read()
                if len(output) > 0:
                    print(output)

    def loadPulpFiles(self, file, data=None):
        """ load and execute all commands in file pulp separate for \n """
        print(
            "\n"
            + display_messages(
                "mode: {}".format(setcolor("script", "ciano", True)), info=True
            )
        )
        if path.isfile(file):
            with open(file, "r") as f:
                data = f.read()
                f.close()
            if data != None:
                print(
                    display_messages("plugin: {}".format(file), info=True, sublime=True)
                )
                return self.onecmd(data, separator="\n")
        print(
            display_messages(
                "script {} not found! ".format(file), error=True, sublime=True
            )
        )
        sys.exit(1)

    def onecmd(self, commands, separator=";"):
        """ load command separate for ; file or string"""
        for command in commands.split(separator):
            Cmd.onecmd(self, command)

    def show_help_command(self, filename):
        """read content file help command """
        print(Linux.readFileHelp(filename))

    def precmd(self, line):
        newline = line.strip()
        is_cmt = newline.startswith("#")
        if is_cmt:
            return ""
        return line

    def postcmd(self, stop, line):
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def do_exit(self, args):
        """ exit the program."""
        print("Quitting.")
        raise SystemExit


class ModuleUI(Cmd):
    """ shell console UI """

    _name_module = None
    completions = None
    options = None
    _background_mode = False
    _instance = None

    @classmethod
    def getInstance(cls):
        return cls._instance

    def __init__(self, parse_args=None, root=None):
        self.__class__._instance = weakref.proxy(self)
        self.parse_args = parse_args
        self.root = root
        Cmd.__init__(self)
        self.conf = SettingsINI(C.CONFIG_INI)
        self.setOptions()
        self.set_prompt_modules()

    def setOptions(self):
        if self.parse_args.pulp:
            self.loadPulpFiles(self.parse_args.pulp)
        elif self.parse_args.xpulp:
            self.onecmd(self.parse_args.xpulp, ";")

    def set_background_mode(self, boolean):
        self._background_mode = boolean

    def check_is_background_mode(self):
        if not self._background_mode:
            return
        print(
            display_messages(
                "module: {} running in background".format(
                    setcolor(self._name_module, color="yellow")
                ),
                info=True,
            )
        )
        print(
            display_messages(
                "use {} command displays the status of jobs started".format(
                    setcolor("jobs", color="red")
                ),
                info=True,
            )
        )

    def set_prompt_modules(self):
        self.prompt = "wp3 : {} > ".format(
            setcolor(self.name_module, color="blue", underline=True)
        )

    @property
    def name_module(self):
        return self._name_module

    @name_module.setter
    def name_module(self, name):
        self._name_module = name

    def do_back(self, args):
        """ go back one level"""
        try:
            self.check_is_background_mode()
            if self._background_mode:
                self.root["PumpkinShell"].getInstance().threads["Modules"][
                    self._name_module
                ] = self.getInstance()
            self.root["PumpkinShell"].getInstance().cmdloop("Starting prompt...")
        except IndexError as e:
            sys.exit(0)

    def do_set(self, args):
        """ set options for module """
        try:
            command, value = args.split()[0], args.split()[1]
            if command in self.options.keys():
                self.options[command] = [value, self.options[command][1]]
            else:
                print(
                    display_messages("unknown command: {} ".format(command), error=True)
                )
                print(display_messages("Example : set host 127.0.0.1", info=True))
        except IndexError:
            pass

    def do_options(self, line):
        """ show options of current module"""
        headers_table, output_table = ["Option", "Value", "Description"], []
        for option, value in self.options.items():
            output_table.append([option, value[0], value[1]])
        print(display_messages("Available Options:", info=True, sublime=True))
        return display_tabulate(headers_table, output_table)

    def do_help(self, args):
        """ show this help """
        names = self.get_names()
        cmds_doc = []
        names.sort()
        print(display_messages("Available Commands:", info=True, sublime=True))
        for name in names:
            if name[:3] == "do_":
                pname = name
                cmd = name[3:]
                if getattr(self, name).__doc__:
                    cmds_doc.append((cmd, getattr(self, name).__doc__))
                else:
                    cmds_doc.append((cmd, ""))

        self.stdout.write("    {}	 {}\n".format("Commands", "Description"))
        self.stdout.write("    {}	 {}\n".format("--------", "-----------"))
        for command, doc in cmds_doc:
            if len(doc) > 0:
                self.stdout.write("    {:<10}	{}\n".format(command, doc))
        print("\n")

    def loadPulpFiles(self, file, data=None):
        """ load and execute all commands in file pulp separate for \n """
        if path.isfile(file):
            with open(file, "r") as f:
                data = f.read()
                f.close()
            if data != None:
                self.onecmd(data, separator="\n")
        sys.exit(1)

    def default(self, args=str):
        """ run commands system allow by tool """
        for goodArgs in C.SYSTEMCOMMAND:
            if args.startswith(goodArgs):
                output = popen(args).read()
                if len(output) > 0:
                    print(output)

    def complete_set(self, text, line, begidx, endidx):
        mline = line.partition(" ")[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in self.completions if s.startswith(mline)]

    def emptyline(self):
        """ Do nothing on empty input line"""
        pass

    def onecmd(self, commands, separator=";"):
        """ load command separate for ; file or string"""
        for command in commands.split(separator):
            Cmd.onecmd(self, command)

    def show_help_command(self, filename):
        """read content file help command """
        print(Linux.readFileHelp(filename))

    def do_exit(self, args):
        sys.exit(0)


class ExtensionUI(Cmd):
    """ native extension console UI """

    _name_module = None
    completions = None
    options = None

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        self.conf = SettingsINI.getInstance()
        Cmd.__init__(self)

    @property
    def name_module(self):
        return self._name_module

    @name_module.setter
    def name_module(self, name):
        self._name_module = name

    def register_command(self, name_func, func):
        """register a command on super class Pumpkinshell """
        setattr(self.root.__class__, name_func, staticmethod(func))

    def show_help_command(self, filename):
        """read content file help command """
        print(Linux.readFileHelp(filename))
