# coding: utf-8
"""
dhcplib.constants
=================
DHCP mappings and constant values.

Legal
-----
This file is part of libpydhcpserver.
libpydhcpserver is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

(C) Jan Segre, 2017 <jan@ispflex.com>
(C) Neil Tallim, 2014 <flan@uguu.ca>
(C) Mathieu Ignacio, 2008 <mignacio@april.org>
"""
TYPE_IPV4 = "ipv4" #: Four bytes in network-byte-order.
TYPE_IPV4_PLUS = "ipv4+" #: At least one multiple of four bytes in network-byte-order.
TYPE_IPV4_MULT = "ipv4*" #: Multiples of four bytes in network-byte-order.
TYPE_BYTE = "byte" #: A single byte.
TYPE_BYTE_PLUS = "byte+" #: At least one byte.
TYPE_STRING = "string" #: Any number of bytes.
TYPE_BOOL = "bool" #: A single byte, constrained to the values 0 (false) and 1 (true).
TYPE_INT = "16-bits" #: Two bytes in network-byte-order.
TYPE_INT_PLUS = "16-bits+" #: At least one multiple of two bytes in network-byte-order.
TYPE_LONG = "32-bits" #: Four bytes in network-byte-order.
TYPE_LONG_PLUS = "32-bits+" #: At least one multiple of four bytes in network-byte-order.
TYPE_IDENTIFIER = "identifier" #: Two bytes in small-endian order.
TYPE_NONE = "none" #: A zero-length sequence.

FIELD_OP = "op" #: The DHCP operation type (Request or Response).
FIELD_HTYPE = "htype" #: The type of hardware involved.
FIELD_HLEN = "hlen" #: The length of the hardware address.
FIELD_HOPS = "hops" #: The number of hops across which the packet has been transmitted.
FIELD_XID = "xid" #: The transaction ID.
FIELD_SECS = "secs" #: The number of seconds that have elapsed since the packet was first emitted.
FIELD_FLAGS = "flags" #: DHCP flags set on the packet.
FIELD_CIADDR = "ciaddr" #: The client's address.
FIELD_YIADDR = "yiaddr" #: The issued address.
FIELD_SIADDR = "siaddr" #: The server's address.
FIELD_GIADDR = "giaddr" #: The gateway's address.
FIELD_CHADDR = "chaddr" #: The hardware address.
FIELD_SNAME = "sname" #: BOOTP server hostname.
FIELD_FILE = "file" #: BOOTP filename.

MAGIC_COOKIE = b'\x63\x82\x53\x63' #: The DHCP magic cookie, per RFC 1048.

DHCP_OP_NAMES = {
    0: 'ERROR_UNDEF',
    1: 'BOOTREQUEST',
    2: 'BOOTREPLY',
} #: Mapping from DHCP operation types to human-readable names.
DHCP_TYPE_NAMES = {
    0: 'ERROR_UNDEF',
    1: 'DHCP_DISCOVER', 2: 'DHCP_OFFER',
    3: 'DHCP_REQUEST', 4:'DHCP_DECLINE',
    5: 'DHCP_ACK', 6: 'DHCP_NAK',
    7: 'DHCP_RELEASE',
    8: 'DHCP_INFORM',
    9: 'DHCP_FORCERENEW',
    10: 'DHCP_LEASEQUERY', 11: 'DHCP_LEASEUNASSIGNED',
    12: 'DHCP_LEASEUNKNOWN', 13: 'DHCP_LEASEACTIVE',
} #: Mapping from DHCP option values to human-readable names.

DHCP_FIELDS = {
    FIELD_OP: (0, 1),
    FIELD_HTYPE: (1, 1),
    FIELD_HLEN: (2, 1),
    FIELD_HOPS: (3, 1),
    FIELD_XID: (4, 4),
    FIELD_SECS: (8, 2),
    FIELD_FLAGS: (10, 2),
    FIELD_CIADDR: (12, 4),
    FIELD_YIADDR: (16, 4),
    FIELD_SIADDR: (20, 4),
    FIELD_GIADDR: (24, 4),
    FIELD_CHADDR: (28, 6),
    FIELD_SNAME: (44, 64),
    FIELD_FILE: (108, 128),
} #: Byte-offset and size definitions for DHCP fields.

DHCP_FIELDS_TEXT = (
    FIELD_SNAME,
    FIELD_FILE,
) #: All DHCP fields for which data should be padded as needed

DHCP_FIELDS_SPECS = {
    TYPE_IPV4: (4, 0, 1), TYPE_IPV4_PLUS: (0, 4, 4), TYPE_IPV4_MULT: (0, 0, 4),
    TYPE_BYTE: (1, 0, 1), TYPE_BYTE_PLUS: (0, 1, 1),
    TYPE_STRING: (0, 0, 1),
    TYPE_BOOL: (1, 0, 1),
    TYPE_INT: (2, 0, 1), TYPE_INT_PLUS: (0, 2, 2),
    TYPE_LONG: (4, 0, 1), TYPE_LONG_PLUS: (0, 4, 4),
    TYPE_IDENTIFIER: (0, 2, 1),
    TYPE_NONE: (0, 0, 1),
}
"""
Information about how to validate basic DHCP types.

The human-readable format-name is mapped against a
(fixed_length, minimum_length, multiple) tuple, which is handled by the
following pseudocode::

if fixed_length == 0:
        if (
            len(value) < minimum_length or
            len(value) % (multiple * minimum_length) != 0
        ):
            fail
    elif len(value) != fixed_length:
        fail
"""

DHCP_FIELDS_TYPES = {
    FIELD_OP: TYPE_BYTE,
    FIELD_HTYPE: TYPE_BYTE,
    FIELD_HLEN: TYPE_BYTE,
    FIELD_HOPS: TYPE_BYTE,
    FIELD_XID: TYPE_LONG,
    FIELD_SECS: TYPE_INT,
    FIELD_FLAGS: TYPE_INT,
    FIELD_CIADDR: TYPE_IPV4,
    FIELD_YIADDR: TYPE_IPV4,
    FIELD_SIADDR: TYPE_IPV4,
    FIELD_GIADDR: TYPE_IPV4,
    FIELD_CHADDR: "hwmac",
    FIELD_SNAME: TYPE_STRING,
    FIELD_FILE: TYPE_STRING,
} #: Maps human-readable field-names to DHCP fields specs.

DHCP_OPTIONS_TYPES = {
    #0: PAD
    1: TYPE_IPV4,
    2: TYPE_LONG,
    3: TYPE_IPV4_PLUS,
    4: TYPE_IPV4_PLUS,
    5: TYPE_IPV4_PLUS,
    6: TYPE_IPV4_PLUS,
    7: TYPE_IPV4_PLUS,
    8: TYPE_IPV4_PLUS,
    9: TYPE_IPV4_PLUS,
    10: TYPE_IPV4_PLUS,
    11: TYPE_IPV4_PLUS,
    12: TYPE_STRING,
    13: TYPE_INT,
    14: TYPE_STRING,
    15: TYPE_STRING,
    16: TYPE_IPV4,
    17: TYPE_STRING,
    18: TYPE_STRING,
    19: TYPE_BOOL,
    20: TYPE_BOOL,
    21: TYPE_IPV4_PLUS,
    22: TYPE_INT,
    23: TYPE_BYTE,
    24: TYPE_LONG,
    25: TYPE_INT_PLUS,
    26: TYPE_INT,
    27: TYPE_BOOL,
    28: TYPE_IPV4,
    29: TYPE_BOOL,
    30: TYPE_BOOL,
    31: TYPE_BOOL,
    32: TYPE_IPV4,
    33: TYPE_IPV4_PLUS,
    34: TYPE_BOOL,
    35: TYPE_LONG,
    36: TYPE_BOOL,
    37: TYPE_BYTE,
    38: TYPE_LONG,
    39: TYPE_BOOL,
    40: TYPE_STRING,
    41: TYPE_IPV4_PLUS,
    42: TYPE_IPV4_PLUS,
    43: TYPE_BYTE_PLUS,
    44: TYPE_IPV4_PLUS,
    45: TYPE_IPV4_PLUS,
    46: TYPE_BYTE,
    47: TYPE_STRING,
    48: TYPE_IPV4_PLUS,
    49: TYPE_IPV4_PLUS,
    50: TYPE_IPV4,
    51: TYPE_LONG,
    52: TYPE_BYTE,
    53: TYPE_BYTE,
    54: TYPE_IPV4,
    55: TYPE_BYTE_PLUS,
    56: TYPE_STRING,
    57: TYPE_INT,
    58: TYPE_LONG,
    59: TYPE_LONG,
    60: TYPE_STRING,
    61: TYPE_IDENTIFIER,
    62: TYPE_STRING,
    63: TYPE_BYTE_PLUS,
    64: TYPE_STRING,
    65: TYPE_IPV4_PLUS,
    66: TYPE_STRING,
    67: TYPE_STRING,
    68: TYPE_IPV4_MULT,
    69: TYPE_IPV4_PLUS,
    70: TYPE_IPV4_PLUS,
    71: TYPE_IPV4_PLUS,
    72: TYPE_IPV4_PLUS,
    73: TYPE_IPV4_PLUS,
    74: TYPE_IPV4_PLUS,
    75: TYPE_IPV4_PLUS,
    76: TYPE_IPV4_PLUS,
    77: TYPE_STRING,
    78: "RFC2610_78", #Implemented
    79: "RFC2610_79", #Implemented
    80: TYPE_NONE,
    81: TYPE_STRING,
    82: TYPE_BYTE_PLUS,
    83: "RFC4174_83", #Implemented
    84: "Unassigned",
    85: TYPE_IPV4_PLUS,
    86: TYPE_BYTE_PLUS,
    87: TYPE_BYTE_PLUS,
    88: "RFC4280_88", #Implemented
    89: TYPE_IPV4_PLUS,
    90: "RFC3118_90", #Not implemented; not necessary for static model
    91: TYPE_LONG,
    92: TYPE_IPV4_PLUS,
    93: TYPE_INT_PLUS,
    94: TYPE_BYTE_PLUS,
    95: TYPE_STRING, #Specifications not published
    96: "Unassigned",
    97: TYPE_BYTE_PLUS,
    98: TYPE_STRING,
    99: TYPE_BYTE_PLUS,
    100: TYPE_STRING,
    101: TYPE_STRING,
    102: "Unassigned", 103: "Unassigned", 104: "Unassigned", 105: "Unassigned",
    106: "Unassigned", 107: "Unassigned", 108: "Unassigned", 109: "Unassigned",
    110: "Unassigned", 111: "Unassigned",
    112: TYPE_STRING, #Specifications not published
    113: TYPE_STRING, #Specifications not published
    114: TYPE_STRING, #Specifications not published
    115: "Unassigned",
    116: TYPE_BOOL,
    117: TYPE_INT_PLUS,
    118: TYPE_IPV4,
    119: "RFC3397_119", #Implemented
    120: "RFC3361_120", #Implemented
    121: "RFC3442_121", #Implemented
    122: TYPE_STRING,
    123: TYPE_BYTE_PLUS,
    124: TYPE_STRING,
    125: TYPE_STRING,
    126: "Unassigned", 127: "Unassigned",
    128: TYPE_STRING,
    129: TYPE_STRING,
    130: TYPE_STRING,
    131: TYPE_STRING,
    132: TYPE_STRING,
    133: TYPE_STRING,
    134: TYPE_STRING,
    135: TYPE_STRING,
    136: TYPE_IPV4_PLUS,
    137: "RFC5223_137", #Implemented
    138: TYPE_IPV4_PLUS,
    139: "RFC5678_139", #Implemented
    140: "RFC5678_140", #Implemented
    141: "Unassigned", 142: "Unassigned", 143: "Unassigned", 144: "Unassigned",
    145: "Unassigned", 146: "Unassigned", 147: "Unassigned", 148: "Unassigned",
    149: "Unassigned",
    150: "Unassigned", #TFTP server address
    151: "Unassigned", 152: "Unassigned", 153: "Unassigned", 154: "Unassigned",
    155: "Unassigned", 156: "Unassigned", 157: "Unassigned", 158: "Unassigned",
    159: "Unassigned", 160: "Unassigned", 161: "Unassigned", 162: "Unassigned",
    163: "Unassigned", 164: "Unassigned", 165: "Unassigned", 166: "Unassigned",
    167: "Unassigned", 168: "Unassigned", 169: "Unassigned", 170: "Unassigned",
    171: "Unassigned", 172: "Unassigned", 173: "Unassigned", 174: "Unassigned",
    175: TYPE_STRING,
    176: "Unassigned", #IP Telephone
    177: "Unassigned", #Etherboot
    178: "Unassigned", 179: "Unassigned", 180: "Unassigned", 181: "Unassigned",
    182: "Unassigned", 183: "Unassigned", 184: "Unassigned", 185: "Unassigned",
    186: "Unassigned", 187: "Unassigned", 188: "Unassigned", 189: "Unassigned",
    190: "Unassigned", 191: "Unassigned", 192: "Unassigned", 193: "Unassigned",
    194: "Unassigned", 195: "Unassigned", 196: "Unassigned", 197: "Unassigned",
    198: "Unassigned", 199: "Unassigned", 200: "Unassigned", 201: "Unassigned",
    202: "Unassigned", 203: "Unassigned", 204: "Unassigned", 205: "Unassigned",
    206: "Unassigned", 207: "Unassigned",
    208: TYPE_LONG,
    209: TYPE_STRING,
    210: TYPE_STRING,
    211: TYPE_LONG,
    212: "Unassigned", 213: "Unassigned", 214: "Unassigned", 215: "Unassigned",
    216: "Unassigned", 217: "Unassigned", 218: "Unassigned", 219: "Unassigned",
    220: "Unassigned", #Subnet Allocation Option
    221: "Unassigned", #Virtual Subnet Selection Option
    222: "Unassigned", 223: "Unassigned",
    224: "Reserved", 225: "Reserved", 226: "Reserved", 227: "Reserved",
    228: "Reserved", 229: "Reserved", 230: "Reserved", 231: "Reserved",
    232: "Reserved", 233: "Reserved", 234: "Reserved", 235: "Reserved",
    236: "Reserved", 237: "Reserved", 238: "Reserved", 239: "Reserved",
    240: "Reserved", 241: "Reserved", 242: "Reserved", 243: "Reserved",
    244: "Reserved", 245: "Reserved", 246: "Reserved", 247: "Reserved",
    248: "Reserved", 249: "Reserved", 250: "Reserved", 251: "Reserved",
    252: "Reserved", 253: "Reserved", 254: "Reserved",
    #255: END
}
"""
Maps DHCP option-numbers to DHCP fields specs.

All values derived from http://www.iana.org/assignments/bootp-dhcp-parameters
"""

DHCP_OPTIONS = {
    #'pad': 0,
    #Vendor extensions
    'subnet_mask': 1,
    'time_offset': 2,
    'router': 3,
    'time_server': 4,
    'name_server': 5,
    'domain_name_servers': 6,
    'log_server': 7,
    'cookie_server': 8,
    'lpr_server': 9,
    'impress_server': 10,
    'resource_location_server': 11,
    'hostname': 12,
    'bootfile': 13,
    'merit_dump_file': 14,
    'domain_name': 15,
    'swap_server': 16,
    'root_path': 17,
    'extensions_path': 18,
    #IP-layer parameters per host
    'ip_forwarding': 19,
    'nonlocal_source_routing': 20,
    'policy_filter': 21,
    'maximum_datagram_reassembly_size': 22,
    'default_ip_time-to-live': 23,
    'path_mtu_aging_timeout': 24,
    'path_mtu_table': 25,
    #IP-layer parameters per interface
    'interface_mtu': 26,
    'all_subnets_are_local': 27,
    'broadcast_address': 28,
    'perform_mask_discovery': 29,
    'mask_supplier': 30,
    'perform_router_discovery': 31,
    'router_solicitation_address': 32,
    'static_routes': 33,
    #Link-layer parameters per interface
    'trailer_encapsulation': 34,
    'arp_cache_timeout': 35,
    'ethernet_encapsulation': 36,
    #TCP parameters
    'tcp_default_ttl': 37,
    'tcp_keepalive_interval': 38,
    'tcp_keepalive_garbage': 39,
    #Applications and service parameters
    'nis_domain': 40,
    'nis_servers': 41,
    'ntp_servers': 42,
    'vendor_specific_information': 43,
    'nbns': 44,
    'nbdd': 45,'nb_node_type': 46,
    'nb_scope': 47,
    'x_window_system_font_server': 48,
    'x_window_system_display_manager': 49,
    #DHCP extensions
    'requested_ip_address': 50,
    'ip_address_lease_time': 51,
    'overload': 52,
    'dhcp_message_type': 53,
    'server_identifier': 54,
    'parameter_request_list': 55,
    'message': 56,
    'maximum_dhcp_message_size': 57,
    'renewal_time_value': 58,
    'rebinding_time_value': 59,
    'vendor_class_identifier': 60,
    'client_identifier': 61,
    #RFC 2132
    'netware_ip_domain_name': 62,
    'netware_ip_sub_options': 63,
    'nis+_domain': 64,
    'nis+_servers': 65,
    'tftp_server_name': 66,
    'bootfile_name': 67,
    'mobile_ip_home_agent': 68,
    'smtp_servers': 69,
    'pop_servers': 70,
    'nntp_servers': 71,
    'default_www_server': 72,
    'default_finger_server': 73,
    'default_irc_server': 74,
    'streettalk_server': 75,
    'streettalk_directory_assistance_server': 76,
    'user_class': 77,
    'directory_agent': 78,
    'service_scope': 79,
    'rapid_commit': 80,
    'client_fqdn': 81,
    'relay_agent': 82,
    'internet_storage_name_service': 83,
    #hole
    'nds_server': 85,
    'nds_tree_name': 86,
    'nds_context': 87,
    'bcmcs_domain_list': 88,
    'bcmcs_ipv4_list': 89,
    'authentication': 90,
    'client_last_transaction_time': 91,
    'associated_ip': 92,
    'client_system': 93,
    'client_ndi': 94,
    'ldap': 95,
    #hole
    'uuid_guid': 97,
    'open_group_user_auth': 98,
    'geoconf_civic': 99,
    'pcode': 100,
    'tcode': 101,
    #hole
    'netinfo_address': 112,
    'netinfo_tag': 113,
    'url': 114,
    #hole
    'auto_config': 116,
    'name_service_search': 117,
    'subnet_selection': 118,
    'domain_search': 119,
    'sip_servers': 120,
    'classless_static_route': 121,
    'cablelabs_client_configuration': 122,
    'geoconf': 123,
    'vendor_class': 124,
    'vendor_specific': 125,
    #hole
    'pxe_128': 128,
    'pxe_129': 129,
    'pxe_130': 130,
    'pxe_131': 131,
    'pxe_132': 132,
    'pxe_133': 133,
    'pxe_134': 134,
    'pxe_135': 135,
    'pana_agent': 136,
    'v4_lost': 137,
    'capwap_ac_v4': 138,
    'ipv4_mos': 139,
    'fqdn_mos': 140,
    #hole
    'ipxe_test': 175,
    #hole
    'pxelinux_magic': 208,
    'configuration_file': 209,
    'path_prefix': 210,
    'reboot_time': 211,
    #hole
    #'end': 255
} #: Maps human-readable DHCP option names to integer values.

DHCP_OPTIONS_REVERSE = {v: k for (k, v) in DHCP_OPTIONS.items()} #: Maps integer values to human-readable DHCP option names.
