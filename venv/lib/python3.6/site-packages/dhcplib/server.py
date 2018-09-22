import logging

from .packet import DHCPPacket

log = logging.getLogger(__name__)


class DHCPProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        #message = data.decode()
        packet = DHCPPacket(data)
        log.debug('RECV from %s:\n%s\n', addr, packet)
        send = False
        if packet.is_dhcp_discover_packet():
            log.debug('DISCOVER')
            packet.transform_to_dhcp_offer_packet()
            packet.set_option('yiaddr', '10.99.0.100')
            packet.set_option('ip_address_lease_time', 60)
            packet.delete_option('hostname')
            send = True
        elif packet.is_dhcp_request_packet():
            log.debug('REQUEST')
            #packet.transform_to_dhcp_nak_packet()
            packet.transform_to_dhcp_ack_packet()
            packet.set_option('yiaddr', '10.99.0.100')
            packet.set_option('router', ['10.99.0.1'], validate=False)
            packet.set_option('domain_name_servers', ['8.8.8.8', '8.8.4.4'], validate=False)
            packet.set_option('ip_address_lease_time', 60)
            packet.delete_option('hostname')
            send = True
        if send:
            log.debug('SEND to %s:\n%s\n', addr, packet)
            ipaddr, port = addr
            if ipaddr == '0.0.0.0':
                ipaddr = '255.255.255.255'
            addr = (ipaddr, port)
            #self.responder.sendto(packet.encode_packet(), addr)
            self.transport.sendto(packet.encode_packet(), addr)

    def error_received(exc):
        log.error('ERROR', exc_info=exc)
