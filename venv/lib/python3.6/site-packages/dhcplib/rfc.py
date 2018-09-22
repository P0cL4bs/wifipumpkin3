# coding: utf-8
"""
dhcplib.rfc
===========
Provides a number of convenience-classes and methods for working with RFC
extensions to the DHCP spec.

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
"""
from ipaddress import IPv4Address
from .conversion import (int_to_list, long_to_list)


def rfc3046_decode(s):
    """
    Extracts sub-options from an RFC3046 option (82).

    :param sequence s: The option's raw data.
    :return dict: The sub-options, as byte-lists, keyed by ID.
    """
    sub_options = {}
    while s:
        id = s.pop(0)
        length = s.pop(0)
        sub_options[id] = s[:length]
        s = s[length:]
    return sub_options


def rfc3925_decode(s, identifier_size=4):
    """
    Extracts sub-options from an RFC3925 option (124, 125 (with
    identifier_size=1)).

    You probably want to use :func:`rfc3925_125_decode` when dealing
    with option 125 specifically.

    :param sequence s: The option's raw data.
    :param int identifier_size: The width of the identifier in bytes.
    :return dict: A dictionary of data as strings keyed by ID numbers.
    """
    data = {}
    while s:
        enterprise_number = conversion.listToNumber(s[:identifier_size])
        payload_size = s[identifier_size]
        payload = s[1 + identifier_size:1 + identifier_size + payload_size]
        s = s[1 + identifier_size + payload_size:]
        data[enterprise_number] = payload
    return data


def rfc3925_125_decode(l):
    """
    Extracts sub-options from an RFC3925 option (125).

    :param sequence s: The option's raw data.
    :return dict: A dictionary of data as dictionaries mapping data as strings
        keyed by ID numbers.
    """
    value = rfc3925_decode(value, identifier_size=4)
    for i in value:
        value[i] = rfc3925_decode(value[i], identifier_size=1)
    return value


def _rfc1035Parse(domain_name):
    """
    Splits an FQDN on dots, outputting data like
    ['g', 'o', 'o', 'g', 'l', 'e', 2, 'c', 'a', 0], in conformance with
    RFC1035.

    :param str domain_name: The FQDN to be converted.
    :return list: The converted FQDN.
    """
    bytes = []
    for fragment in domain_name.split('.'):
        bytes += [len(fragment)] + [ord(c) for c in fragment]
    return bytes + [0]


class RFC:
    """
    A generic special RFC object, used to simplify the process of setting
    complex options.
    """
    _value = None #: The bytes associated with this object.

    def get_value(self):
        """
        Provides the type's data as a list of bytes.

        Note that this is the actual internal list; modifications to the list
        will be persistent.

        :return list: A list of bytes.
        """
        return self._value

    def __repr__(self):
        return "<%(name)s : %(value)r>" % {
            'name': self.__class__.__name__,
            'value': self._value,
        }

    def __nonzero__(self):
        return 1

    def __cmp__(self, other):
        """
        If ``other`` is an RFC instance, their values are compared. Otherwise,
        the internal list's value is compared directly to ``other``.
        """
        if isinstance(other, RFC):
            return cmp(self._value, other.get_value())
        return cmp(self._value, other)


class rfc1035_plus(RFC):
    def __init__(self, data):
        """
        Formats FQDNs as an RFC1035-formatted sequence.

        :param str data: The comma-delimited FQDNs to process.
        """
        self._value = []
        for token in (tok for tok in (t.strip() for t in data.split(',')) if tok):
            self._value += _rfc1035Parse(token)


class rfc2610_78(RFC):
    def __init__(self, mandatory, data):
        """
        Formats native IPv4s as encoded IPv4 addresses.

        :param bool mandatory: True if the IPv4 addresses have to be respected.
        :param str data: The comma-delimited IPv4s to process.
        """
        self._value = [int(mandatory)]
        for token in (tok for tok in (t.strip() for t in data.split(',')) if tok):
            self._value.extend(IPv4Address(token).packed)


class rfc2610_79(RFC):
    def __init__(self, mandatory, data):
        """
        Formats scope-list data.

        :param bool mandatory: True if the scope-list has to be respected.
        :param str data: The scope-list to process.
        """
        self._value = [int(mandatory)] + [ord(c) for c in data.encode('utf-8')]


class rfc3361_120(RFC):
    def __init__(self, data):
        """
        Formats the given data into multiple IPv4 addresses or
        RFC1035-formatted strings.

        :param str data: The comma-delimited IPv4s or FQDNs to process.
        :except ValueError: Both IPv4s and FQDNs were provided.
        """
        ip_4_mode = False
        dns_mode = False

        self._value = []
        for token in (tok for tok in (t.strip() for t in data.split(',')) if tok):
            try:
                self._value.extend(IPv4Address(token).token)
                ip_4_mode = True
            except ValueError:
                self._value += _rfc1035Parse(token)
                dns_mode = True

        if ip_4_mode == dns_mode:
            raise ValueError("'%(data)s contains both IPv4 and DNS-based entries" % {
                'data': data,
            })

        self._value.insert(0, int(ip_4_mode))


class rfc3397_119(rfc1035_plus):
    pass


class rfc3442_121(RFC):
    def __init__(self, classless_addresses):
        """
        Accepts a sequence of CIDR entries and routers to produce classless
        static route byte-blocks.

        You'll probably want to put (("0.0.0.0", 0), packet.getOption("router"))
        at the start to ensure the default gateway is set as expected.

        :param classless_addresses: ((network IPv4, CIDR-mask), router IPv4)
            elements, like (("169.254.0.0", 16), "0.0.0.0").
        :except ValueError: An illegal address or mask was encountered.
        """
        self._value = []
        for ((ip, mask), router) in classless_addresses:
            ip = IPv4Address(ip)
            router = IPv4Address(router)
            if not 0 <= mask <= 32:
                raise ValueError("CIDR mask %(mask)i is not between 0 and 32" % {
                    'mask': mask,
                })
            width = mask / 8
            if mask % 8:
                width += 1

            self._value.append(mask)
            if width:
                self._value.extend(tuple(ip.packed)[:width])
            self._value.extend(router.packed)


class rfc3925_124(RFC):
    def __init__(self, data):
        """
        Sets `vendor_class` data.

        :param dict data: A dictionary of data-strings keyed by ID-ints.
        """
        self._value = []
        for (enterprise_number, payload) in sorted(data.items()):
            self._value += long_to_list(enterprise_number)
            self._value.append(chr(len(payload)))
            self._value += payload


class rfc3925_125(RFC):
    def __init__(self, data):
        """
        Sets `vendor_specific` data.

        :param dict data: A dictionary of dictionaries of data-strings, keyed
            by ID-ints at both levels.
        """
        self._value = []
        for (enterprise_number, payload) in sorted(data.items()):
            self._value += long_to_list(enterprise_number)

            subdata = []
            for (subopt_code, subpayload) in sorted(payload.items()):
                subdata.append(chr(subopt_code))
                subdata.append(chr(len(subpayload)))
                subdata += subpayload

            self._value.append(chr(len(subdata)))
            self._value += subdata


class rfc4174_83(RFC):
    def __init__(self, isns_functions, dd_access, admin_flags, isns_security, ips):
        """
        Sets iSNS configuration parameters.

        :param int isns_functions: A sixteen-bit value.
        :param int dd_access: A sixteen-bit value.
        :param int admin_flags: A sixteen-bit value.
        :param int isns_security: A thirty-two-bit value.
        :param str ips: Comma-delimited IPv4s to be processed.
        """
        isns_functions = int_to_list(isns_functions)
        dd_access = int_to_list(dd_access)
        admin_flags = int_to_list(admin_flags)
        isns_security = long_to_list(isns_security)

        self._value = isns_functions + dd_access + admin_flags + isns_security
        for token in [tok for tok in [t.strip() for t in ips.split(',')] if tok]:
            self._value.extend(IPv4Address(token).packed)


class rfc4280_88(rfc1035_plus):
    pass


class rfc5223_137(rfc1035_plus):
    pass


class rfc5678_139(RFC):
    def __init__(self, values):
        """
        Formats the given data into multiple IPv4 addresses associated with
        sub-option codes.

        :param sequence values: A sequence of (code:int, IPv4s:string) elements.
        """
        self._value = []
        for (code, addresses) in values:
            self._value.append(code)
            for token in [tok for tok in [address.strip() for address in addresses.split(',')] if tok]:
                self._value.extend(IPv4Address(token).packed)


class rfc5678_140(RFC):
    def __init__(self, values):
        """
        Formats the given data into multiple RFC1035-formatted strings
        associated with sub-option codes.

        :param sequence values: A sequence of (code:int, FQDNs:string)
            elements.
        """
        self._value = []
        for (code, addresses) in values:
            self._value.append(code)
            self._value += rfc1035_plus(addresses).get_value()
