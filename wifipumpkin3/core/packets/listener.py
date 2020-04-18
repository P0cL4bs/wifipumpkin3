from socket import *
import struct
import base64
import select

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

# see https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol
# section DHCP options


def inet_ntoaX(data):
    return [".".join(map(str, data[i : i + 4])) for i in range(0, len(data), 4)]


def inet_atonX(ips):
    return b"".join(map(inet_aton, ips))


dhcp_message_types = {
    1: "DHCPDISCOVER",
    2: "DHCPOFFER",
    3: "DHCPREQUEST",
    4: "DHCPDECLINE",
    5: "DHCPACK",
    6: "DHCPNAK",
    7: "DHCPRELEASE",
    8: "DHCPINFORM",
}
reversed_dhcp_message_types = dict()
for i, v in dhcp_message_types.items():
    reversed_dhcp_message_types[v] = i

shortunpack = lambda data: (data[0] << 8) + data[1]
shortpack = lambda i: bytes([i >> 8, i & 255])


def macunpack(data):
    s = base64.b16encode(data)
    return ":".join([s[i : i + 2].decode("ascii") for i in range(0, 12, 2)])


def macpack(mac):
    return base64.b16decode(mac.replace(":", "").replace("-", "").encode("ascii"))


def unpackbool(data):
    return data[0]


def packbool(bool):
    return bytes([bool])


options = [
    # RFC1497 vendor extensions
    ("pad", None, None),
    ("subnet_mask", inet_ntoa, inet_aton),
    ("time_offset", None, None),
    ("router", inet_ntoaX, inet_atonX),
    ("time_server", inet_ntoaX, inet_atonX),
    ("name_server", inet_ntoaX, inet_atonX),
    ("domain_name_server", inet_ntoaX, inet_atonX),
    ("log_server", inet_ntoaX, inet_atonX),
    ("cookie_server", inet_ntoaX, inet_atonX),
    ("lpr_server", inet_ntoaX, inet_atonX),
    ("impress_server", inet_ntoaX, inet_atonX),
    ("resource_location_server", inet_ntoaX, inet_atonX),
    ("host_name", lambda d: d.decode("ASCII"), lambda d: d.encode("ASCII")),
    ("boot_file_size", None, None),
    ("merit_dump_file", None, None),
    ("domain_name", None, None),
    ("swap_server", inet_ntoa, inet_aton),
    ("root_path", None, None),
    ("extensions_path", None, None),
    # IP Layer Parameters per Host
    ("ip_forwarding_enabled", unpackbool, packbool),
    ("non_local_source_routing_enabled", unpackbool, packbool),
    ("policy_filer", None, None),
    ("maximum_datagram_reassembly_size", shortunpack, shortpack),
    ("default_ip_time_to_live", lambda data: data[0], lambda i: bytes([i])),
    ("path_mtu_aging_timeout", None, None),
    ("path_mtu_plateau_table", None, None),
    # IP Layer Parameters per Interface
    ("interface_mtu", None, None),
    ("all_subnets_are_local", unpackbool, packbool),
    ("broadcast_address", inet_ntoa, inet_aton),
    ("perform_mask_discovery", unpackbool, packbool),
    ("mask_supplier", None, None),
    ("perform_router_discovery", None, None),
    ("router_solicitation_address", inet_ntoa, inet_aton),
    ("static_route", None, None),
    # Link Layer Parameters per Interface
    ("trailer_encapsulation_option", None, None),
    ("arp_cache_timeout", None, None),
    ("ethernet_encapsulation", None, None),
    # TCP Parameters
    ("tcp_default_ttl", None, None),
    ("tcp_keep_alive_interval", None, None),
    ("tcp_keep_alive_garbage", None, None),
    # Application and Service Parameters Part 1
    ("network_information_service_domain", None, None),
    ("network_informtaion_servers", inet_ntoaX, inet_atonX),
    ("network_time_protocol_servers", inet_ntoaX, inet_atonX),
    ("vendor_specific_information", None, None),
    ("netbios_over_tcp_ip_name_server", inet_ntoaX, inet_atonX),
    ("netbios_over_tcp_ip_datagram_distribution_server", inet_ntoaX, inet_atonX),
    ("netbios_over_tcp_ip_node_type", None, None),
    ("netbios_over_tcp_ip_scope", None, None),
    ("x_window_system_font_server", inet_ntoaX, inet_atonX),
    ("x_window_system_display_manager", inet_ntoaX, inet_atonX),
    # DHCP Extensions
    ("requested_ip_address", inet_ntoa, inet_aton),
    (
        "ip_address_lease_time",
        lambda d: struct.unpack(">I", d)[0],
        lambda i: struct.pack(">I", i),
    ),
    ("option_overload", None, None),
    (
        "dhcp_message_type",
        lambda data: dhcp_message_types.get(data[0], data[0]),
        (lambda name: bytes([reversed_dhcp_message_types.get(name, name)])),
    ),
    ("server_identifier", inet_ntoa, inet_aton),
    ("parameter_request_list", list, bytes),
    ("message", None, None),
    ("maximum_dhcp_message_size", shortunpack, shortpack),
    ("renewal_time_value", None, None),
    ("rebinding_time_value", None, None),
    ("vendor_class_identifier", None, None),
    ("client_identifier", macunpack, macpack),
    ("tftp_server_name", None, None),
    ("boot_file_name", None, None),
    # Application and Service Parameters Part 2
    ("network_information_service_domain", None, None),
    ("network_information_servers", inet_ntoaX, inet_atonX),
    ("", None, None),
    ("", None, None),
    ("mobile_ip_home_agent", inet_ntoaX, inet_atonX),
    ("smtp_server", inet_ntoaX, inet_atonX),
    ("pop_servers", inet_ntoaX, inet_atonX),
    ("nntp_server", inet_ntoaX, inet_atonX),
    ("default_www_server", inet_ntoaX, inet_atonX),
    ("default_finger_server", inet_ntoaX, inet_atonX),
    ("default_irc_server", inet_ntoaX, inet_atonX),
    ("streettalk_server", inet_ntoaX, inet_atonX),
    ("stda_server", inet_ntoaX, inet_atonX),
]

assert options[18][0] == "extensions_path", options[18][0]
assert options[25][0] == "path_mtu_plateau_table", options[25][0]
assert options[33][0] == "static_route", options[33][0]
assert options[50][0] == "requested_ip_address", options[50][0]
assert options[64][0] == "network_information_service_domain", options[64][0]
assert options[76][0] == "stda_server", options[76][0]


class ReadBootProtocolPacket(object):
    for i, o in enumerate(options):
        locals()[o[0]] = None
        locals()["option_{0}".format(i)] = None

    del i, o

    def __init__(self, data, address=("0.0.0.0", 0)):
        self.data = data
        self.address = address
        self.host = address[0]
        self.port = address[1]

        # wireshark = wikipedia = data[...]

        self.message_type = self.OP = data[0]
        self.hardware_type = self.HTYPE = data[1]
        self.hardware_address_length = self.HLEN = data[2]
        self.hops = self.HOPS = data[3]

        self.XID = self.transaction_id = struct.unpack(">I", data[4:8])[0]

        self.seconds_elapsed = self.SECS = shortunpack(data[8:10])
        self.bootp_flags = self.FLAGS = shortunpack(data[8:10])

        self.client_ip_address = self.CIADDR = inet_ntoa(data[12:16])
        self.your_ip_address = self.YIADDR = inet_ntoa(data[16:20])
        self.next_server_ip_address = self.SIADDR = inet_ntoa(data[20:24])
        self.relay_agent_ip_address = self.GIADDR = inet_ntoa(data[24:28])

        self.client_mac_address = self.CHADDR = macunpack(
            data[28 : 28 + self.hardware_address_length]
        )
        index = 236
        self.magic_cookie = self.magic_cookie = inet_ntoa(data[index : index + 4])
        index += 4
        self.options = dict()
        self.named_options = dict()
        while index < len(data):
            option = data[index]
            index += 1
            if option == 0:
                # padding
                # Can be used to pad other options so that they are aligned to the word boundary; is not followed by length byte
                continue
            if option == 255:
                # end
                break
            option_length = data[index]
            index += 1
            option_data = data[index : index + option_length]
            index += option_length
            self.options[option] = option_data
            if option < len(options):
                option_name, function, _ = options[option]
                if function:
                    option_data = function(option_data)
                if option_name:
                    setattr(self, option_name, option_data)
                    self.named_options[option_name] = option_data
            setattr(self, "option_{}".format(option), option_data)

    def __getitem__(self, key):
        print(key, dir(self))
        return getattr(self, key, None)

    def __contains__(self, key):
        return key in self.__dict__

    @property
    def formatted_named_options(self):
        return "\n".join(
            "{}:\t{}".format(name.replace("_", " "), value)
            for name, value in sorted(self.named_options.items())
        )

    def __str__(self):
        return """Message Type: {self.message_type}
client MAC address: {self.client_mac_address}
client IP address: {self.client_ip_address}
your IP address: {self.your_ip_address}
next server IP address: {self.next_server_ip_address}
{self.formatted_named_options}
""".format(
            self=self
        )

    def __gt__(self, other):
        return id(self) < id(other)


data = base64.b16decode(
    b"02010600f7b41ad100000000c0a800640000000000000000000000007c7a914bca6c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501053604c0a800010104ffffff000304c0a800010604c0a80001ff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000".upper()
)
assert data[0] == 2
p = ReadBootProtocolPacket(data)
assert p.message_type == 2
assert p.hardware_type == 1
assert p.hardware_address_length == 6
assert p.hops == 0
assert p.transaction_id == 4155775697
assert p.seconds_elapsed == 0
assert p.bootp_flags == 0
assert p.client_ip_address == "192.168.0.100"
assert p.your_ip_address == "0.0.0.0"
assert p.next_server_ip_address == "0.0.0.0"
assert p.relay_agent_ip_address == "0.0.0.0"
assert p.client_mac_address.lower() == "7c:7a:91:4b:ca:6c"
assert p.magic_cookie == "99.130.83.99"
assert p.dhcp_message_type == "DHCPACK"
assert p.options[53] == b"\x05"
assert p.server_identifier == "192.168.0.1"
assert p.subnet_mask == "255.255.255.0"
assert p.router == ["192.168.0.1"]
assert p.domain_name_server == ["192.168.0.1"]
str(p)

if __name__ == "__main__":
    s1 = socket(type=SOCK_DGRAM)
    s1.setsockopt(SOL_IP, SO_REUSEADDR, 1)
    s1.bind(("", 67))
    # s2 = socket(type = SOCK_DGRAM)
    # s2.setsockopt(SOL_IP, SO_REUSEADDR, 1)
    # s2.bind(('', 68))
    while 1:
        reads = select.select([s1], [], [], 1)[0]
        for s in reads:
            packet = ReadBootProtocolPacket(*s.recvfrom(4096))
            print(packet)
