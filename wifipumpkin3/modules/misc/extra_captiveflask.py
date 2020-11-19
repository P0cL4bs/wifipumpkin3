from wifipumpkin3.core.common.terminal import ModuleUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.printer import (
    display_messages,
    setcolor,
    display_tabulate,
)
import tempfile
import requests
from os import path
from zipfile import ZipFile
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI
from distutils.dir_util import copy_tree
from shutil import copyfile

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


class ModPump(ModuleUI):
    """ Extra customs captiveflask templates """

    name = "extra_captiveflask"

    save_path = tempfile.gettempdir() + "/master.zip"
    extracted_filepath = tempfile.gettempdir() + "/extra-captiveflask-master"
    config_file_ini = tempfile.gettempdir() + "/extra-captiveflask-master/config.ini"
    captiveflask_path = "wifipumpkin3/plugins/captiveflask"

    config_default = SettingsINI(C.CONFIG_CP_INI_ROOT)

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        self.name_module = self.name

        self.plugins_remote = {}
        self.table_headers = ["Name", "Author", "Installed", "Preview"]
        super(ModPump, self).__init__(parse_args=self.parse_args, root=self.root)

    def do_list(self, args):
        """ show all avaliable templates from github """
        if not path.isfile(self.save_path):
            print(
                display_messages(
                    "can't find downloaded file: {}".format(self.save_path), error=True
                )
            )
            return

        config = SettingsINI(self.config_file_ini)

        plugins_installed = self.config_default.get_all_childname("plugins")

        self.plugins_remote = {}
        for plugin in config.get_all_childname("plugins"):
            self.plugins_remote[plugin] = {}
            for info in config.get_all_childname("info_{}".format(plugin)):
                self.plugins_remote[plugin][info] = config.get(
                    "info_{}".format(plugin), info
                )

            self.plugins_remote[plugin]["installed"] = (
                setcolor("True", color="green")
                if plugin in plugins_installed
                else setcolor("False", color="red")
            )

        self.table_output = []
        for plugin in self.plugins_remote:
            self.table_output.append(
                [
                    self.plugins_remote[plugin]["name"],
                    self.plugins_remote[plugin]["author"],
                    self.plugins_remote[plugin]["installed"],
                    self.plugins_remote[plugin]["preview"],
                ]
            )
        if len(self.table_output) > 0:
            print(
                display_messages(
                    "Available Customs CaptiveFlask:", info=True, sublime=True
                )
            )
            display_tabulate(self.table_headers, self.table_output)

    def do_download(self, args):
        """ download all avaliable templates"""
        url = C.URL_EXTRA_CAPTIVEFLASK
        chunk_size = 128
        print(
            display_messages(
                "downloading templates on {} ".format(self.save_path), info=True
            )
        )
        try:
            r = requests.get(url, stream=True)
        except Exception as e:
            print(display_messages(e, error=True))
            return

        with open(self.save_path, "wb") as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)

        if not path.isfile(self.save_path):
            print(display_messages("error when try download templates", error=True))
            return
        print(display_messages("extra captiveflask download successful.", sucess=True))

        print(display_messages("extracting files from zip archive", info=True))
        path_to_zip_file = tempfile.gettempdir() + "/master.zip"
        with ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extractall(tempfile.gettempdir())

        print(
            display_messages(
                "extracted files on : {}".format(self.extracted_filepath), info=True
            )
        )

    def installPluginByName(self, plugin_name):
        print(
            display_messages(
                "Install plugin:: {}".format(setcolor(plugin_name, color="yellow")),
                info=True,
                sublime=True,
            )
        )
        source = "{}/plugins/{}.py".format(self.extracted_filepath, plugin_name)
        destination = "{}/{}.py".format(self.captiveflask_path, plugin_name)
        dest = copyfile(source, destination)
        print(display_messages("copy content file to {}".format(dest), info=True))

        folder_plugin = "{}/templates/{}".format(self.extracted_filepath, plugin_name)
        copy_tree(folder_plugin, "config/templates/{}".format(plugin_name))
        print(
            display_messages(
                "copy content directory to {}".format(
                    "config/templates/{}".format(plugin_name)
                ),
                info=True,
            )
        )

        self.config_default.set("plugins", plugin_name, False)
        config = SettingsINI(self.config_file_ini)
        if config.get_all_childname("set_{}".format(plugin_name)) != []:
            for language in config.get_all_childname("set_{}".format(plugin_name)):
                self.config_default.set("set_{}".format(plugin_name), language, False)
            self.config_default.set("set_{}".format(plugin_name), "Default", True)

        print(
            display_messages(
                "plugin install {}".format(setcolor("sucessful", color="green")),
                info=True,
            )
        )

    def do_install(self, args):
        """ install custom captiveflask portals """
        if not path.isdir(self.captiveflask_path):
            print(
                display_messages(
                    "directory {} not found".format(self.captiveflask_path), error=True
                )
            )
            return

        if args:
            plugin_name = args.split()[0]
            if not plugin_name in self.plugins_remote:
                print(
                    display_messages(
                        "plugin: {} not found ".format(plugin_name), error=True
                    )
                )
                return
            self.installPluginByName(plugin_name)
            return self.show_help_command("help_extra_captiveflask")

        anwer_question = input("So, do you want to install all plugins ? (Y/N): ")
        if anwer_question.lower() != "y":
            return

        for plugin in self.plugins_remote:
            self.installPluginByName(plugin)

        return self.show_help_command("help_extra_captiveflask")

    def do_info(self, args):
        """ get info custom captiveflask portals """
        if args:
            plugin_name = args.split()[0]
            if not plugin_name in self.plugins_remote:
                print(
                    display_messages(
                        "plugin: {} not found ".format(plugin_name), error=True
                    )
                )
                return
            print(display_messages("Information", info=True, sublime=True))
            list_keys = [
                "Name",
                "Author",
                "Version",
                "Installed",
                "Preview",
                "Description",
            ]
            for item in list_keys:
                print(
                    " {} : {}".format(
                        setcolor(item, color="blue"),
                        setcolor(
                            self.plugins_remote[plugin_name][item.lower()],
                            color="yellow",
                        ),
                    )
                )
            print("\n")

    def complete_info(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.plugins_remote.keys())
                if command.startswith(text)
            ]
        else:
            return list(self.plugins_remote.keys())

    def complete_install(self, text, args, start_index, end_index):
        if text:
            return [
                command
                for command in list(self.plugins_remote.keys())
                if command.startswith(text)
            ]
        else:
            return list(self.plugins_remote.keys())

    def do_options(self, line):
        pass

    def do_set(self, args):
        pass
