# coding: utf-8
"""
dhcplib.net
===========
Handles send/receive and internal routing for DHCP packets.

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
(C) Matthew Boedicker, 2011 <matthewm@boedicker.org>
(C) Mathieu Ignacio, 2008 <mignacio@april.org>
"""
import array
import collections
import select
import socket
import struct
import threading
from ipaddress import IPv4Address

from .mac import MAC
from .packet import (DHCPPacket, FLAGBIT_BROADCAST)
from .constants import (
    FIELD_CIADDR, FIELD_YIADDR, FIELD_SIADDR, FIELD_GIADDR,
)

#IP constants
_IP_GLOB = IPv4Address('0.0.0.0') #: The internal "everything" address.
_IP_BROADCAST = IPv4Address('255.255.255.255') #: The broadcast address.
IP_UNSPECIFIED_FILTER = (_IP_GLOB, _IP_BROADCAST, None) #: A tuple of addresses that reflect non-unicast targets.

_ETH_P_SNAP = 0x0005
"""
Internal-only Ethernet-frame-grabbing for Linux.

Nothing should be addressable to the special response socket, but better to avoid wasting memory.
"""

Address = collections.namedtuple("Address", ('ip', 'port'))
"""
An inet layer-3 address.

.. py:attribute:: ip

An :class:`IPv4Address <ipaddress.IPv4Address>` address

.. py:attribute:: port

A numeric port value.
"""


class DHCPServer:
    """
    Handles internal packet-path-routing logic.
    """
    _server_address = None #: The IP associated with this server.
    _network_link = None #: The I/O-handler; you don't want to touch this.

    def __init__(self, server_address, server_port, client_port, proxy_port=None, response_interface=None, response_interface_qtags=None):
        """
        Sets up the DHCP network infrastructure.

        :param server_address: The IP address on which to run the DHCP service.
        :type server_address: :class:`IPv4Address <ipaddress.IPv4Address>`
        :param int port: The port on which DHCP servers and relays listen in this network.
        :param int client_port: The port on which DHCP clients listen in this network.
        :param int proxy_port: The port on which ProxyDHCP servers listen for in
            this network; ``None`` to disable.
        :param str response_interface: The interface on which to provide raw packet support,
            like ``"eth0"``, or ``None`` if not requested. ``'-'`` enables automatic resolution
            based on `server_address`.
        :param sequence response_interface_qtags: Any qtags to insert into raw packets, in
            order of appearance. Definitions take the following form:
            (pcp:`0-7`, dei:``bool``, vid:`1-4094`)
        :except Exception: A problem occurred during setup.
        """
        self._server_address = server_address
        if response_interface == '-':
            from . import getifaddrslib
            response_interface = getifaddrslib.get_network_interface(server_address)
        self._network_link = NetworkLink(str(server_address), server_port, client_port, proxy_port, response_interface, response_interface_qtags=response_interface_qtags)

    def _select_handler(packet):
        if packet.is_dhcp_request_packet():
            return self._handle_dhcp_request
        elif packet.is_dhcp_discover_packet():
            return self._handle_dhcp_discover
        elif packet.is_dhcp_inform_packet():
            return self._handle_dhcp_inform
        elif packet.is_dhcp_release_packet():
            return self._handle_dhcp_release
        elif packet.is_dhcp_decline_packet():
            return self._handle_dhcp_decline
        elif packet.is_dhcp_lease_query_packet():
            return self._handle_dhcp_lease_query

    def _get_next_dhcp_packet(self, timeout=60, packet_buffer=2048):
        """
        Blocks for up to ``timeout`` seconds while waiting for a packet to
        arrive; if one does, a thread is spawned to process it.

        Have a thread blocking on this at all times; restart it immediately after it returns.

        :param int timeout: The number of seconds to wait before returning.
        :param int packet_buffer: The size of the buffer to use for receiving packets.
        :return tuple(2): (DHCP-packet-received:``bool``,
                          :class:`Address <dhcp.Address>` or ``None`` on
                          timeout)
        """
        (source_address, data, port) = self._network_link.get_data(timeout=timeout, packet_buffer=packet_buffer)
        if data:
            try:
                packet = DHCPPacket(data=data)
            except ValueError:
                pass
            else:
                handler = self._select_handler(packet)
                threading.Thread(target=handler, args=(packet, source_address, port)).start()
                return (True, source_address)
        return (False, source_address)

    def _handle_dhcp_decline(self, packet, source_address, port):
        """
        Processes a DECLINE packet.

        Override this with your own logic to handle DECLINEs.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        """

    def _handle_dhcp_discover(self, packet, source_address, port):
        """
        Processes a DISCOVER packet.

        Override this with your own logic to handle DISCOVERs.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        """

    def _handle_dhcp_inform(self, packet, source_address, port):
        """
        Processes an INFORM packet.

        Override this with your own logic to handle INFORMs.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        """

    def _handle_dhcp_lease_query(self, packet, source_address, port):
        """
        Processes a LEASEQUERY packet.

        Override this with your own logic to handle LEASEQUERYs.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        """

    def _handle_dhcp_release(self, packet, source_address, port):
        """
        Processes a RELEASE packet.

        Override this with your own logic to handle RELEASEs.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        """

    def _handle_dhcp_request(self, packet, source_address, port):
        """
        Processes a REQUEST packet.

        Override this with your own logic to handle REQUESTs.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        """

    def _send_dhcp_packet(self, packet, source_address, port):
        """
        Encodes and sends a DHCP packet to its destination.

        **Important**: during this process, the packet may be modified, but
        will be restored to its initial state by the time this method returns.
        If any threadsafing is required, it must be handled in calling logic.

        :param packet: The packet to be processed.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param source_address: The address from which the request was received.
        :type source_address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        :return int: The number of bytes transmitted.
        :except Exception: A problem occurred during serialisation or
            transmission.
        """
        return self._network_link.send_data(packet, source_address, port)


class NetworkLink:
    """
    Handles network I/O.
    """
    _client_port = None #: The port on which clients expect to receive DHCP traffic.
    _server_port = None #: The port on which servers expect to receive DHCP traffic.
    _proxy_port = None #: The port on which ProxyDHCP traffic is expected to be exchanged.
    _proxy_socket = None #: The internal socket to use for ProxyDHCP traffic.
    _responder_dhcp = None #: The internal socket to use for responding to DHCP requests.
    _responder_proxy = None #: The internal socket to use for responding to ProxyDHCP requests.
    _responder_broadcast = None #: The internal socket to use for responding to broadcast requests.
    _listening_sockets = None #: All sockets on which to listen for activity.
    _unicast_discover_supported = False #: Whether unicast responses to DISCOVERs are supported.

    def __init__(self, server_address, server_port, client_port, proxy_port=None, response_interface=None, response_interface_qtags=None):
        """
        Sets up the DHCP network infrastructure.

        :param str server_address: The IP address on which to run the DHCP service.
        :param int server_port: The port on which DHCP servers and relays listen in this network.
        :param int client_port: The port on which DHCP clients listen in this network.
        :param int|None proxy_port: The port on which DHCP servers listen for ProxyDHCP traffic in
            this network.
        :param str|None response_interface: The interface on which to provide raw packet support,
            like 'eth0', or None if not requested.
        :param sequence|None response_interface_qtags: Any qtags to insert into raw packets, in
            order of appearance. Definitions take the following form:
            (pcp:`0-7`, dei:``bool``, vid:`1-4094`)
        :except Exception: A problem occurred during setup.
        """
        self._client_port = client_port
        self._server_port = server_port
        self._proxy_port = proxy_port

        #Create and bind unicast sockets
        (dhcp_socket, proxy_socket) = self._setup_listening_sockets(server_port, proxy_port, server_address)
        if proxy_socket:
            self._listening_sockets = (dhcp_socket, proxy_socket)
            self._proxy_socket = proxy_socket
        else:
            self._listening_sockets = (dhcp_socket,)

        #Wrap the sockets with appropriate logic and set options
        self._responder_dhcp = _L3Responder(socketobj=dhcp_socket)
        self._responder_proxy = _L3Responder(socketobj=proxy_socket)
        #Either create a raw-response socket or a generic broadcast-response socket
        if response_interface:
            try:
                self._responder_broadcast = _L2Responder_AF_PACKET(server_address, response_interface, qtags=response_interface_qtags)
            except Exception:
                try:
                    self._responder_broadcast = _L2Responder_pcap(server_address, response_interface, qtags=response_interface_qtags)
                except Exception as e:
                    import errno
                    raise EnvironmentError(errno.ELIBACC, "Raw response-socket requested on %(interface)s, but neither AF_PACKET nor libpcap are available, or the interface does not exist" % {'interface': response_interface,})
            self._unicast_discover_supported = True
        else:
            self._responder_broadcast = _L3Responder(server_address=server_address)

    def _setup_listening_sockets(self, server_port, proxy_port, server_address=None):
        """
        Creates and binds the listening sockets.

        :param int server_port: The port on which to listen for DHCP traffic.
        :param int proxy_port: The port on which to listen for ProxyDHCP traffic.
        :param string server_address: The IP address to listen for DHCP traffic on
        :return tuple(2): The DHCP and ProxyDHCP sockets, the latter of which may be ``None`` if
            not requested.
        :except socket.error: Sockets could not be created or bound.
        """
        dhcp_socket = proxy_socket = None
        try:
            dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if proxy_port:
                proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            raise Exception('Unable to create socket: %s' % e)

        try:
            dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if proxy_socket:
                proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as e:
            import warnings
            warnings.warn('Unable to set SO_REUSEADDR; multiple DHCP servers cannot be run in parallel: %s' % e)

        try:
            dhcp_socket.bind(('', server_port))
            if proxy_port:
                proxy_socket.bind(('', proxy_port))
        except socket.error as e:
            raise Exception('Unable to bind sockets: %s' % e)

        if server_address:
            from . import getifaddrslib
            listen_interface = getifaddrslib.get_network_interface(server_address)
            try:
                dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, listen_interface)
            except socket.error as e:
                raise OSError(msg.errno, 'Unable to limit listening to %(listen_interface)s: %(err)s' % {
                    'listen_interface': listen_interface,
                    'err': e.strerror,
                })

        return (dhcp_socket, proxy_socket)

    def get_data(self, timeout, packet_buffer):
        """
        Runs `select()` over all relevant sockets, providing data if available.

        :param int timeout: The number of seconds to wait before returning.
        :param int packet_buffer: The size of the buffer to use for receiving packets.
        :return tuple(3):
            0. :class:`Address <dhcp.Address>` or ``None``: None if the timeout was reached.
            1. The received data as a ``str`` or ``None`` if the timeout was reached.
            2. the port on which the packet was received; -1 on timeout or error.
        :except select.error: The `select()` operation did not complete gracefully.
        """
        port = -1
        active_sockets = select.select(self._listening_sockets, [], [], timeout)[0]
        if active_sockets:
            active_socket = active_sockets[0]
            if active_socket == self._proxy_socket:
                port = self._proxy_port
            else:
                port = self._server_port
            (data, source_address) = active_socket.recvfrom(packet_buffer)
            if data:
                return (Address(IPv4Address(source_address[0]), source_address[1]), data, port)
        return (None, None, port)

    def send_data(self, packet, address, port):
        """
        Writes the packet to to appropriate socket, addressed to the appropriate recipient.

        :param packet: The packet to be written.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param address: The address from which the original packet was received.
        :type address: :class:`Address <dhcp.Address>`
        :param int port: The port on which the packet was received.
        :return tuple(2):
            0. The number of bytes written to the network.
            1. The :class:`Address <dhcp.Address>` ultimately used.
        :except Exception: A problem occurred during serialisation or transmission.
        """
        ip = None
        relayed = False
        port = self._client_port
        source_port = self._server_port
        responder = self._responder_dhcp
        if address.ip in IP_UNSPECIFIED_FILTER: #Broadcast source; this is never valid for ProxyDHCP
            if (not self._unicast_discover_supported #All responses have to be via broadcast
                    or packet.getFlag(FLAGBIT_BROADCAST)): #Broadcast bit set; respond in kind
                ip = _IP_BROADCAST
            else: #The client wants unicast and this host can handle it
                #Try to get the client's address first, falling back to broadcast if missing
                ip = packet.extractIPOrNone(FIELD_YIADDR) or _IP_BROADCAST
            responder = self._responder_broadcast
        else: #Unicast source
            ip = address.ip
            relayed = bool(packet.extractIPOrNone(FIELD_GIADDR))
            if relayed: #Relayed request.
                port = self._server_port
            else: #Request directly from client, routed or otherwise.
                if port == self._proxy_port:
                    ip = packet.extractIPOrNone(FIELD_CIADDR) or ip
                    port = address.port or port #BSD doesn't seem to preserve port information
                    source_port = port
                    responder = self._responder_proxy

        return responder.send(packet, ip, port, relayed, source_port=source_port)


class _Responder(object):
    """
    A generic responder-template, which defines common logic.
    """
    def send(self, packet, ip, port, relayed, **kwargs):
        """
        Performs final sanity-checking and address manipulation, then submits the packet for
        transmission.

        :param packet: The packet to be written.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param ip: The address to which the packet should be sent.
        :type ip: :class:`IPv4Address <ipaddress.IPv4Address>`
        :param int port: The port to which the packet should be sent.
        :param bool relayed: ``True`` if the packet came from a relay.
        :param \*\*kwargs: Any technology-specific arguments.
        :return tuple(2):
            0. The number of bytes written to the network.
            1. The :class:`Address <dhcp.Address>` ultimately used.
        :except Exception: An error occurred during serialisation or transmission.
        """
        if relayed:
            broadcast_source = packet.extractIPOrNone(FIELD_CIADDR) in IP_UNSPECIFIED_FILTER
        else:
            broadcast_source = ip in IP_UNSPECIFIED_FILTER
        (broadcast_changed, original_was_broadcast) = packet.setFlag(FLAGBIT_BROADCAST, broadcast_source)

        #Perform any necessary packet-specific address-changes
        if not original_was_broadcast: #Unicast behaviour permitted; use the packet's IP override, if set
            ip = packet.response_ip or ip
        port = packet.response_port or port
        if packet.response_source_port is not None:
            kwargs['source_port'] = packet.response_source_port

        bytes_sent = self._send(packet, str(ip), port, **kwargs)
        if broadcast_changed: #Restore the broadcast bit, in case the packet needs to be used for something else
            packet.setFlag(FLAGBIT_BROADCAST, original_was_broadcast)
        return (bytes_sent, Address(IPv4Address(ip), port))

    def _send(self, packet, ip, port, **kwargs):
        """
        Handles technology-specific transmission; must be implemented by subclasses.

        :param packet: The packet to be written.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param ip: The address to which the packet should be sent.
        :type ip: :class:`IPv4Address <dhcp_types.IPv4Address>`
        :param int port: The port to which the packet should be sent.
        :param \*\*kwargs: Any technology-specific arguments.
        :return int: The number of bytes written to the network.
        :except Exception: An error occurred during serialisation or transmission.
        """
        raise NotImplementedError("_send() must be implemented in subclasses")


class _L3Responder(_Responder):
    """
    Defines rules and logic needed to respond at layer 3.
    """
    _socket = None #: The socket used for responses.

    def __init__(self, socketobj=None, server_address=None):
        """
        Wraps an existing socket or creates an arbitrarily bound new socket with broadcast
        capabilities.

        :param socket.socket|None socketobj: The socket to be bound; if ``None``, a new one is
            created.
        :param str|None server_address: The address to which a new socket should be bound.
        :except Exception: Unable to bind a new socket.
        """
        if socketobj:
            self._socket = socketobj
        else:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            try:
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            except socket.error as e:
                raise Exception('Unable to set SO_BROADCAST: %s' % e)

            try:
                self._socket.bind((server_address or '', 0))
            except socket.error as e:
                raise Exception('Unable to bind socket: %s' % e)

    def _send(self, packet, ip, port, **kwargs):
        """
        Serialises and sends the packet.

        :param packet: The packet to be written.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param str ip: The address to which the packet should be sent.
        :param int port: The port to which the packet should be sent.
        :param \*\*kwargs: Any technology-specific arguments.
        :return int: The number of bytes written to the network.
        :except Exception: An error occurred during serialisation or transmission.
        """
        return self._socket.sendto(packet.encode_packet(), (ip, port))


class _L2Responder(_Responder):
    """
    Defines rules and logic needed to respond at layer 2.
    """
    _ethernet_id = None #: The source MAC and Ethernet payload-type (and qtags, if applicable).
    _server_address = None #: The server's IP.

    def __init__(self, server_address, mac, qtags=None):
        """
        Constructs the Ethernet header for all L2 communication.

        :param str server_address: The server's IP as a dotted quad.
        :param str mac: The MAC of the responding interface, in network-byte order.
        :param sequence qtags: Any qtags to insert into raw packets, in order of appearance.
            Definitions take the following form: (pcp:`0-7`, dei:``bool``, vid:`1-4094`)
        """

        self._server_address = socket.inet_aton(str(server_address))
        ethernet_id = [mac,] #Source MAC
        if qtags:
            for (pcp, dei, vid) in qtags:
                ethernet_id.append("\x81\x00") #qtag payload-type
                qtag_value = pcp << 13 #Priority-code-point (0-7)
                qtag_value += int(dei) << 12 #Drop-eligible-indicator
                qtag_value += vid #vlan-identifier
                ethernet_id.append(self._pack('!H', qtag_value))
        ethernet_id.append("\x08\x00") #IP payload-type
        self._ethernet_id = ''.join(ethernet_id)

    def _checksum(self, data):
        """
        Computes the RFC768 checksum of ``data``.

        :param sequence data: The data to be checksummed.
        :return int: The data's checksum.
        """
        if sum(len(i) for i in data) & 1: #Odd
            checksum = sum(array.array('H', ''.join(data)[:-1]))
            checksum += ord(data[-1][-1]) #Add the final byte
        else: #Even
            checksum = sum(array.array('H', ''.join(data)))
        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum += (checksum >> 16)
        return ~checksum & 0xffff

    def _ip_checksum(self, ip_prefix, ip_destination):
        """
        Computes the checksum of the IPv4 header.

        :param str ip_prefix: The portion of the IPv4 header preceding the `checksum` field.
        :param str ip_destination: The destination address, in network-byte order.
        :return int: The IPv4 checksum.
        """
        return self._checksum([
            ip_prefix,
            '\0\0', #Empty checksum field
            self._server_address,
            ip_destination,
        ])

    def _udp_checksum(self, ip_destination, udp_addressing, udp_length, packet):
        """
        Computes the checksum of the UDP header and payload.

        :param str ip_destination: The destination address, in network-byte order.
        :param str udp_addressing: The UDP header's port section.
        :param str udp_length: The length of the UDP payload plus header.
        :param str packet: The serialised packet.
        :return int: The UDP checksum.
        """
        return self._checksum([
            self._server_address,
            ip_destination,
            '\0\x11', #UDP spec padding and protocol
            udp_length,
            udp_addressing,
            udp_length,
            '\0\0', #Dummy UDP checksum
            packet,
        ])

    def _assemble_packet(self, packet, mac, ip, port, source_port):
        """
        Assembles the Ethernet, IPv4, and UDP headers, serialises the packet, and provides a
        complete Ethernet frame for injection into the network.

        :param packet: The packet to be written.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param mac: The MAC to which the packet is addressed.
        :type mac: :class:`MAC <dhcp_types.mac.MAC>`
        :param str ip: The IPv4 to which the packet is addressed, as a dotted quad.
        :param int port: The port to which the packet is addressed.
        :param int source_port: The port from which the packet is addressed.
        :return str: The complete binary packet.
        """
        binary = []

        #<> Ethernet header
        if _IP_BROADCAST == ip:
            binary.append('\xff\xff\xff\xff\xff\xff') #Broadcast MAC
        else:
            binary.append(''.join(chr(i) for i in mac)) #Destination MAC
        binary.append(self._ethernet_id) #Source MAC and Ethernet payload-type

        #<> Prepare packet data for transmission and checksumming
        binary_packet = packet.encode_packet()
        packet_len = len(binary_packet)

        #<> IP header
        binary.append(struct.pack("!BBHHHBB",
                                  69, #IPv4 + length=5
                                  0, #DSCP/ECN aren't relevant
                                  28 + packet_len, #The UDP and packet lengths in bytes
                                  0, #ID, which is always 0 because we're the origin
                                  packet_len <= 560 and 0b0100000000000000 or 0, #Flags and fragmentation
                                  128, #Make the default TTL sane, but not maximum
                                  0x11, #Protocol=UDP
                                  ))
        ip_destination = socket.inet_aton(ip)
        binary.extend((
            struct.pack("<H", self._ip_checksum(binary[-1], ip_destination)),
            self._server_address,
            ip_destination
        ))

        #<> UDP header
        binary.append(struct.pack("!HH", source_port, port))
        binary.append(struct.pack("!H", packet_len + 8)) #8 for the header itself
        binary.append(struct.pack("<H", self._udp_checksum(ip_destination, binary[-2], binary[-1], binary_packet)))

        #<> Payload
        binary.append(binary_packet)

        return ''.join(binary)

    def _send(self, packet, ip, port, source_port=0, **kwargs):
        """
        Serialises and sends the packet.

        :param packet: The packet to be written.
        :type packet: :class:`DHCPPacket <dhcp_types.packet.DHCPPacket>`
        :param str ip: The address to which the packet should be sent.
        :param int port: The port to which the packet should be sent.
        :param int source_port: The UDP port from which to claim the packet originated.
        :param \*\*kwargs: Any technology-specific arguments.
        :return int: The number of bytes written to the network.
        :except Exception: An error occurred during serialisation or transmission.
        """
        mac = (packet.response_mac and MAC(packet.response_mac)) or packet.get_hardware_address()
        binary_packet = self._assemble_packet(packet, mac, ip, port, source_port)
        return self._send_(binary_packet)


class _L2Responder_AF_PACKET(_L2Responder):
    """
    A Linux-specific layer 2 responder that uses AF_PACKET.
    """
    _socket = None #: The socket used for responses.

    def __init__(self, server_address, response_interface, qtags=None):
        """
        Creates and configures a raw socket on an interface.

        :param str server_address: The server's IP as a dotted quad.
        :param str response_interface: The interface on which to provide raw packet support, like
            ``"eth0"``.
        :param sequence qtags: Any qtags to insert into raw packets, in order of appearance.
            Definitions take the following form: (pcp:`0-7`, dei:``bool``, vid:`1-4094`)
        :except socket.error: The socket could not be configured.
        """
        self._socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(_ETH_P_SNAP))
        self._socket.bind((response_interface, _ETH_P_SNAP))
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 ** 12)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 ** 12)

        mac = self._socket.getsockname()[4]
        _L2Responder.__init__(self, server_address, mac, qtags=qtags)

    def _send_(self, packet):
        """
        Sends the packet.

        :param str packet: The packet to be written.
        :return int: The number of bytes written to the network.
        :except Exception: An error occurred during transmission.
        """
        return self._socket.send(packet)


class _L2Responder_pcap(_L2Responder):
    """
    A more general Unix-oriented layer 2 responder that uses libpcap.
    """
    _fd = None #: The file-descriptor of the socket used for responses.
    _inject = None #: The "send" function to invoke from libpcap.

    #Locally cached module functions
    _c_int_ = None #: `ctypes.c_int`

    def __init__(self, server_address, response_interface, qtags=None):
        """
        Creates and configures a raw socket on an interface.

        :param str server_address: The server's IP as a dotted quad.
        :param str response_interface: The interface on which to provide raw packet support, like
            ``"eth0"``.
        :param sequence qtags: Any qtags to insert into raw packets, in order of appearance.
            Definitions take the following form: (pcp:`0-7`, dei:``bool``, vid:`1-4094`)
        :except Exception: Interfacing with libpcap failed.
        """
        import ctypes
        self._c_int_ = ctypes.c_int
        import ctypes.util

        from . import getifaddrslib

        pcap = ctypes.util.find_library('pcap')
        if not pcap:
            raise Exception("libpcap not found")
        pcap = ctypes.cdll.LoadLibrary(pcap)

        errbuf = ctypes.create_string_buffer(256)
        self._fd = pcap.pcap_open_live(response_interface, ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), errbuf)
        if not self._fd:
            import errno
            raise IOError(errno.EACCES, errbuf.value)
        elif errbuf.value:
            import warnings
            warnings.warn(errbuf.value)

        try:
            mac = ''.join(chr(i) for i in MAC(getifaddrslib.get_mac_address(response_interface)))
        except Exception:
            pcap.pcap_close(self._fd)
            raise
        else:
            _L2Responder.__init__(self, server_address, mac, qtags=qtags)
        self._inject = pcap.pcap_inject

    def _send_(self, packet):
        """
        Sends the packet.

        :param str packet: The packet to be written.
        :return int: The number of bytes written to the network.
        :except Exception: An error occurred during transmission.
        """
        return self._inject(self._fd, packet, self._c_int_(len(packet)))
