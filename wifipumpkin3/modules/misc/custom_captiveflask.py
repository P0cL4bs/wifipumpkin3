from wifipumpkin3.core.common.terminal import ModuleUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.printer import (
    display_messages,
    setcolor
)
import tempfile
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
    """Install custom captiveflask templates"""

    name = "custom_captiveflask"

    temp_path = tempfile.gettempdir() 
    captiveflask_setup_path = C.wp3_setup_packager_path + "/plugins/captiveflask"

    config_default = SettingsINI(C.CONFIG_CP_INI_ROOT)

    def __init__(self, parse_args=None, root=None):
        self.parse_args = parse_args
        self.root = root
        self.name_module = self.name

        self.plugins_remote = {}
        self.table_headers = ["Name", "Author", "Installed", "Preview"]
        super(ModPump, self).__init__(parse_args=self.parse_args, root=self.root)

    def do_install(self, args):
        """install captiveflask template by zip file"""
        if args:
            try:
                plugin_name, file_path = args.split()[0], args.split()[1]
            except Exception as e:
                return print(display_messages("the argument is invalid please type ?install for more information", error=True))
            if not path.isfile(file_path):
                return print(
                    display_messages(
                        "the file {} not found ".format(file_path), error=True
                    )
                )
            head, tail = os.path.split(file_path)
            dest = copyfile(file_path, "{}/{}".format(self.temp_path, tail))
            print(display_messages("copy content file .zip to {}".format(dest), info=True))
            
            path_to_zip_file = tempfile.gettempdir() + "/{}".format(tail)
            with ZipFile(path_to_zip_file, "r") as zip_ref:
                zip_ref.extractall(tempfile.gettempdir())
            temp_path_file_extracted = "{}/{}.py".format(self.temp_path, plugin_name)
            print(
                display_messages(
                    "extracted files on : {}".format(temp_path_file_extracted), info=True
                )
            )
            if not path.isfile(temp_path_file_extracted):
                return print(
                    display_messages(
                        "the file {} not found ".format(temp_path_file_extracted), error=True
                    )
                )
            temp_templates_path = "{}/{}".format(self.temp_path, plugin_name)
            if not path.isdir(temp_templates_path):
                return print(
                    display_messages(
                        "the directory template {} not found ".format(temp_templates_path), error=True
                    )
                )
            source = temp_path_file_extracted
            destination = "{}/{}.py".format(self.captiveflask_setup_path, plugin_name)
            dest = copyfile(source, destination)
            print(display_messages("copy content file to {}".format(dest), info=True))

            copy_tree(
                temp_templates_path, C.user_config_dir + "/config/templates/{}".format(plugin_name)
            )
            print(
                display_messages(
                    "plugin {} install {}".format( plugin_name,setcolor("sucessful", color="green")),
                    info=True,
                )
            )
            return 
        print(
            display_messages("unknown command: {} ".format(args), error=True)
        )
        
    def help_install(self):
         self.show_help_command("help_install_customcaptiveflask")
         
    def do_options(self, line):
        pass

    def do_set(self, args):
        pass
