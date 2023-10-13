import os
import wifipumpkin3 as wp3

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

dir_of_executable = os.path.dirname(__file__)
dir_path = os.getcwd()
user_config_dir = os.path.expanduser("~") + "/.config/wifipumpkin3"
wp3_setup_packager_path = wp3.__path__[0]
wp3_path_data = f"{wp3_setup_packager_path}/data"

config_dir_packager_data = [
    f"{wp3_path_data}/config",
    f"/usr/share/wifipumpkin3/data/config", # for .deb kali linux
    f"/usr/wifipumpkin3/data/config", # for .deb debian general
]

SYSTEMCOMMAND = [
    "ifconfig",
    "iw",
    "iwconfig",
    "route",
    "iptables",
    "ls",
    "clear",
    "nano",
]

HELPFILESPATH = wp3_path_data + "/helps/"
EXCEPTFILESPATH = wp3_path_data + "/exceptions/"
APIRESTPATH = user_config_dir + "/api/"

# DHCP logger connected
CLIENTS_CONNECTED = user_config_dir + "/config/session/connected.json"

DHCPSERVERBINARY = "core/packets/binary/dhcpserver"

# DNS file hosts
DNSHOSTS = user_config_dir + "/config/app/dns_hosts.ini"

# donation button
# TODO: add donation in readme
DONATE = "https://github.com/P0cL4bs/wifipumpkin3#donation"
DONATE_TXT = (
    "Consider donating to support the development and maintenance of WiFi-Pumpkin. "
)

# settings DHCP
DHCPLEASES_PATH = "/var/lib/dhcp/dhcpd.leases"
DHCPCONF_PATH = user_config_dir + "/config/dhcpd.conf"

# settings HOSTAPD
HOSTAPDCONF_PATH = user_config_dir + "/config/hostapd/hostapd.conf"
HOSTAPDCONF_PATH2 = user_config_dir + "/config/hostapd/hostapd+.conf"
ALGORITMS = ("TKIP", "CCMP", "TKIP + CCMP")

# system configs
NETWORKMANAGER = "/etc/NetworkManager/NetworkManager.conf"
IPFORWARD = "/proc/sys/net/ipv4/ip_forward"

# Docker settings
DOCKERIPTABLESPATH = "/etc/iptables.ipv4.nat"
DOCKERHOSTAPDCONF_PATH = "/etc/hostapd/hostapd.conf"

# logging
LOG_PUMPKINPROXY = user_config_dir + "/logs/ap/pumpkin_proxy.log"
LOG_EVILQR3PROXY = user_config_dir + "/logs/ap/evilqr3_proxy.log"
LOG_PYDNSSERVER = user_config_dir + "/logs/ap/pydns_server.log"
LOG_PYDHCPSERVER = user_config_dir + "/logs/ap/pydhcp_server.log"
LOG_SNIFFKIN3 = user_config_dir + "/logs/ap/sniffkin3.log"
LOG_PHISHKIN3 = user_config_dir + "/logs/ap/phishkin3.log"
LOG_CAPTIVEPO = user_config_dir + "/logs/ap/captiveportal.log"
LOG_RESPONDER = user_config_dir + "/logs/ap/responder.log"
LOG_HOSTAPD = user_config_dir + "/logs/ap/hostapd.log"
LOG_ALL = user_config_dir + "/logs/everything.log"


LOG_BASE = user_config_dir + "/logs/ap"


ALL_LOGSPATH = (
    LOG_PUMPKINPROXY,
    LOG_PYDNSSERVER,
    LOG_PYDHCPSERVER,
    LOG_SNIFFKIN3,
    LOG_PHISHKIN3,
    LOG_CAPTIVEPO,
    LOG_RESPONDER,
    LOG_HOSTAPD,
    LOG_ALL,
)

# APP SETTINGS
CONFIG_INI = user_config_dir + "/config/app/config.ini"
CONFIG_SK_INI = user_config_dir + "/config/app/sniffkin3.ini"
CONFIG_PP_INI = user_config_dir + "/config/app/pumpkinproxy.ini"
CONFIG_PK_INI = user_config_dir + "/config/app/phishkin3.ini"
CONFIG_EQ_INI = user_config_dir + "/config/app/evilqr3.ini"
CONFIG_CP_INI = user_config_dir + "/config/app/captive-portal.ini"
CONFIG_CP_INI_ROOT = user_config_dir + "/config/app/captive-portal.ini"


ALL_CONFIGSINI = {
    "config": CONFIG_INI,
    "sniffkin3": CONFIG_SK_INI,
    "pumpkinproxy": CONFIG_PP_INI,
    "captiveflask": CONFIG_CP_INI,
    "phishkin3": CONFIG_PK_INI,
}

URL_EXTRA_CAPTIVEFLASK = (
    "https://github.com/mh4x0f/extra-captiveflask/archive/master.zip"
)


TEMPLATES = "templates/fakeupdate/Windows_Update/Settins_WinUpdate.html"
TEMPLATE_PH = "templates/phishing/custom/index.html"
TEMPLATE_CLONE = "templates/phishing/web_server/index.html"
EXTRACT_TEMP = "cd templates/ && tar -xf fakeupdate.tar.gz"
LCOMMITS = "https://raw.githubusercontent.com/P0cL4bs/WiFi-Pumpkin/master/Core/config/commits/Lcommits.cfg"
SOURCE_URL = "https://github.com/P0cL4bs/WiFi-Pumpkin.git"


# settings template
TEMPLATES_FLASK = user_config_dir + "/config/"
TEMP_CUSTOM = dir_path + "/templates/phishing/custom"
TEMP_Win = dir_path + "/templates/fakeupdate/Windows_Update"
TEMP_Java = dir_path + "/templates/fakeupdate/Java_Update"

# plugins path
RESPONDER_EXEC = "plugins/external/Responder/Responder.py"
DNS2PROXY_EXEC = "plugins/external/dns2proxy/dns2proxy.py"
BDFPROXY_EXEC = "plugins/external/BDFProxy-ng/bdf_proxy.py"
