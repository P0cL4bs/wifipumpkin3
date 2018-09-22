# coding: utf-8
"""
dhcplib.getifaddrslib
=====================
Support for resolving an IPv4 address to a network interface and retrieving the
MAC address for an interface by name, in pure, stdlib CPython.

Suitable for use with Linux, FreeBSD, OpenBSD, NetBSD, DragonflyBSD, and
Mac OS X.

Legal
=====
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and via any
medium.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Authors
=======
Neil Tallim <flan@uguu.ca>
"""
import ctypes
import ctypes.util
import socket

#Linux constants that might not be present in Python
_AF_PACKET = (hasattr(socket, 'AF_PACKET') and socket.AF_PACKET) or 17
#BSD constants that might not be present in Python
_AF_LINK = (hasattr(socket, 'AF_LINK') and socket.AF_LINK) or 18

_LIBC = ctypes.CDLL(ctypes.util.find_library('c'))

class struct_sockaddr(ctypes.Structure):
    _fields_ = (
        ('sa_family', ctypes.c_ushort),
    )

class struct_sockaddr_in(ctypes.Structure):
    _fields_ = (
        ('sin_family', ctypes.c_ushort),
        ('sin_port', ctypes.c_uint16),
        ('sin_addr', ctypes.c_ubyte * 4),
    )

class struct_ifaddrs(ctypes.Structure): pass
struct_ifaddrs._fields_ = (
    ('ifa_next', ctypes.POINTER(struct_ifaddrs)),
    ('ifa_name', ctypes.c_char_p),
    ('ifa_flags', ctypes.c_uint32),
    ('ifa_addr', ctypes.POINTER(struct_sockaddr)),
) #Linux diverges from BSD for the rest, but it's safe to omit the tail

#AF_LINK
class struct_sockaddr_dl(ctypes.Structure):
    _fields_ = (
        ('sdl_len', ctypes.c_byte),
        ('sdl_family', ctypes.c_byte),
        ('sdl_index', ctypes.c_ushort),
        ('sdl_type', ctypes.c_ubyte),
        ('sdl_nlen', ctypes.c_ubyte),
        ('sdl_alen', ctypes.c_ubyte),
        ('sdl_slen', ctypes.c_ubyte),
        ('sdl_data', ctypes.c_ubyte * 12),
    )
#AF_PACKET
class struct_sockaddr_ll(ctypes.Structure):
    _fields_ = (
        ('sll_family', ctypes.c_ushort),
        ('sll_protocol', ctypes.c_ushort),
        ('sll_ifindex', ctypes.c_int32),
        ('sll_hatype', ctypes.c_ushort),
        ('sll_pkttype', ctypes.c_ubyte),
        ('sll_halen', ctypes.c_ubyte),
        ('sll_addr', ctypes.c_ubyte * 8),
    )

def _evaluate_ipv4(ifaddr, ipv4):
    sockaddr = ifaddr.ifa_addr.contents
    if sockaddr.sa_family == socket.AF_INET: #IPv4 address
        sockaddr_in = ctypes.cast(ctypes.pointer(sockaddr), ctypes.POINTER(struct_sockaddr_in)).contents
        return socket.inet_ntop(socket.AF_INET, sockaddr_in.sin_addr) == ipv4
    return False

def _extract_ipv4(ifaddr):
    return ifaddr.ifa_name.decode("utf-8")

def _evaluate_mac(ifaddr, iface):
    if ifaddr.ifa_name.decode("utf-8") == iface:
        sockaddr = ifaddr.ifa_addr.contents
        if sockaddr.sa_family == _AF_PACKET:
            return True
        sockaddr_dl = ctypes.cast(ctypes.pointer(sockaddr), ctypes.POINTER(struct_sockaddr_dl)).contents
        return sockaddr_dl.sdl_family == _AF_LINK
    return False

def _extract_mac(ifaddr):
    sockaddr = ifaddr.ifa_addr.contents
    if sockaddr.sa_family == _AF_PACKET:
        sockaddr_ll = ctypes.cast(ctypes.pointer(sockaddr), ctypes.POINTER(struct_sockaddr_ll)).contents
        mac = sockaddr_ll.sll_addr[:sockaddr_ll.sll_halen]
    else:
        sockaddr_dl = ctypes.cast(ctypes.pointer(sockaddr), ctypes.POINTER(struct_sockaddr_dl)).contents
        mac = sockaddr_dl.sdl_data[sockaddr_dl.sdl_nlen:sockaddr_dl.sdl_nlen + sockaddr_dl.sdl_alen]
    return ':'.join('%02x' % b for b in mac)

def _evaluate_ifaddrs(evaluator, extractor):
    ifap = ctypes.POINTER(struct_ifaddrs)()
    if _LIBC.getifaddrs(ctypes.pointer(ifap)): #Non-zero response
        raise OSError(ctypes.get_errno())

    try:
        ifaddr = ifap.contents
        while True:
            if evaluator(ifaddr):
                return extractor(ifaddr)
            if not ifaddr.ifa_next:
                break
            ifaddr = ifaddr.ifa_next.contents
    finally:
        _LIBC.freeifaddrs(ifap)
    return None

def get_network_interface(ipv4):
    ifaddr = _evaluate_ifaddrs(
        lambda ifaddr : _evaluate_ipv4(ifaddr, ipv4),
        _extract_ipv4,
    )
    return ifaddr and ifaddr.encode('ascii')

def get_mac_address(iface):
    ifaddr = _evaluate_ifaddrs(
        lambda ifaddr : _evaluate_mac(ifaddr, iface),
        _extract_mac,
    )
    return ifaddr and ifaddr.encode('ascii')

if __name__ == '__main__':
    import sys
    iface_name = get_network_interface(sys.argv[1])
    print(iface_name)
    print(get_mac_address(iface_name))
