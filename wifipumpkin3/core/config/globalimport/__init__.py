import os
import sys
from pwd import getpwnam
from grp import getgrnam
from PyQt5 import QtCore, Qt
from logging import getLogger,ERROR
# from core.utils import (
#     Refactor,set_monitor_mode,waiterSleepThread,
#     setup_logger,is_ascii,is_hexadecimal,exec_bash,del_item_folder
# )
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI
from wifipumpkin3.core.utility.collection import SettingsINI as SuperSettings
from collections import OrderedDict
from functools import  partial
from wifipumpkin3.core.utility.component import ComponentBlueprint
from netaddr import EUI
from wifipumpkin3.core.utility.printer import display_messages
from wifipumpkin3.core.common.platforms import Linux as Refactor
from wifipumpkin3.core.common.platforms import setup_logger
from wifipumpkin3.core.widgets.default.logger_manager import StandardLog
from wifipumpkin3.core.widgets.default.logger_manager import LoggerManager

def deleteObject(obj):
    ''' reclaim memory '''
    del obj
def ProgramPath(executablename):
    expath = os.popen('which {}'.format(executablename)).read().split('\n')[0]

    if os.path.isfile(expath):
        return expath
    else:
        return False

def get_mac_vendor(mac):
    ''' discovery mac vendor by mac address '''
    try:
        d_vendor = EUI(mac)
        d_vendor = d_vendor.oui.registration().org
    except:
        d_vendor = 'unknown mac'
    return d_vendor


def exec_bash(command):
    ''' run command on background hide output'''
    os.popen(command)


__all__ = ["deleteObject","os","sys","exec_bash","LoggerManager","StandardLog","setup_logger","Qt","QtCore","SuperSettings","getLogger","ERROR",
           "C","OrderedDict","partial","Refactor","ComponentBlueprint","getgrnam",
           "getpwnam","ProgramPath","get_mac_vendor"]

#root = QtCore.QCoreApplication.instance()
#Settings = root.Settings
#__all__.append["Settings"]