from re import findall
import logging
from scapy.all import hexdump
from wifipumpkin3.core.utility.collection import SettingsINI
from PyQt5.QtCore import pyqtSignal
import wifipumpkin3.core.utility.constants as C

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


class PSniffer(object):
    """ plugins data sniffers"""

    name = "plugin sniffkin3 master"
    version = "1.0"
    config = SettingsINI(C.CONFIG_SK_INI)
    loggers = {}
    output = pyqtSignal(object)
    session = None

    def filterPackets(self, pkt):
        """ intercept packetes data """
        raise NotImplementedError

    def get_http_headers(self, http_payload):
        """ get header dict http request"""
        try:
            headers_raw = http_payload[: http_payload.index("\r\n\r\n") + 2]
            headers = dict(findall(r"(?P<name>.*?):(?P<value>.*?)\r\n", headers_raw))
        except:
            return None
        if "Content-Type" not in headers:
            return None

        return headers

    def setup_logger(self, logger_name, log_file, key=str(), level=logging.INFO):
        if self.loggers.get(logger_name):
            return self.loggers.get(logger_name)
        else:
            logger = logging.getLogger(logger_name)
            formatter = logging.Formatter(
                "SessionID[{}] %(asctime)s : %(message)s".format(key)
            )
            fileHandler = logging.FileHandler(log_file, mode="a")
            fileHandler.setFormatter(formatter)
            logger.setLevel(logging.INFO)
            logger.addHandler(fileHandler)
        return logger

    def hexdumpPackets(self, pkt):
        """ show packets hexdump """
        return hexdump(pkt)
