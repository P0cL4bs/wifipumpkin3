import os
import sys
from pwd import getpwnam
from grp import getgrnam
from PyQt5 import QtCore, Qt
from logging import getLogger, ERROR
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI as SuperSettings
from collections import OrderedDict
from functools import partial
from wifipumpkin3.core.utility.printer import (
    display_messages,
    display_tabulate,
    setcolor,
)
from wifipumpkin3.core.common.platforms import Linux as Refactor
from wifipumpkin3.core.widgets.default.logger_manager import StandardLog, LoggerManager

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


def deleteObject(obj):
    """reclaim memory"""
    del obj


def ProgramPath(executablename):
    expath = os.popen("which {}".format(executablename)).read().split("\n")[0]

    if os.path.isfile(expath):
        return expath
    else:
        return False

def exec_bash(command):
    """run command on background hide output"""
    os.popen(command)


__all__ = [
    "deleteObject",
    "os",
    "sys",
    "display_messages",
    "display_tabulate",
    "setcolor",
    "exec_bash",
    "LoggerManager",
    "StandardLog",
    "Qt",
    "QtCore",
    "SuperSettings",
    "getLogger",
    "ERROR",
    "C",
    "OrderedDict",
    "partial",
    "Refactor",
    "getgrnam",
    "getpwnam",
    "ProgramPath",
]

# root = QtCore.QCoreApplication.instance()
# Settings = root.Settings
# __all__.append["Settings"]
