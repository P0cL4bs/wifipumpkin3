from PyQt5.QtCore import QThread,pyqtSignal,QThread,QObject


import json
import logging
import os
import signal
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from time import sleep

from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer


TYPE_LOOKUP = {
    'A': (dns.A, QTYPE.A),
    'AAAA': (dns.AAAA, QTYPE.AAAA),
    'CAA': (dns.CAA, QTYPE.CAA),
    'CNAME': (dns.CNAME, QTYPE.CNAME),
    'DNSKEY': (dns.DNSKEY, QTYPE.DNSKEY),
    'MX': (dns.MX, QTYPE.MX),
    'NAPTR': (dns.NAPTR, QTYPE.NAPTR),
    'NS': (dns.NS, QTYPE.NS),
    'PTR': (dns.PTR, QTYPE.PTR),
    'RRSIG': (dns.RRSIG, QTYPE.RRSIG),
    'SOA': (dns.SOA, QTYPE.SOA),
    'SRV': (dns.SRV, QTYPE.SRV),
    'TXT': (dns.TXT, QTYPE.TXT),
    'SPF': (dns.TXT, QTYPE.TXT),
}

SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())


class Record:
    def __init__(self, rname, rtype, args):
        self._rname = DNSLabel(rname)

        rd_cls, self._rtype = TYPE_LOOKUP[rtype]

        if self._rtype == QTYPE.SOA and len(args) == 2:
            # add sensible times to SOA
            args += (SERIAL_NO, 3600, 3600 * 3, 3600 * 24, 3600),

        if self._rtype == QTYPE.TXT and len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 255:
            # wrap long TXT records as per dnslib's docs.
            args = wrap(args[0], 255),

        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            ttl = 3600 * 24
        else:
            ttl = 300

        self.rr = RR(
            rname=self._rname,
            rtype=self._rtype,
            rdata=rd_cls(*args),
            ttl=ttl,
        )

    def match(self, q):
        return q.qname == self._rname and (q.qtype == QTYPE.ANY or q.qtype == self._rtype)

    def sub_match(self, q):
        return self._rtype == QTYPE.SOA and q.qname.matchSuffix(self._rname)

    def __str__(self):
        return str(self.rr)


class Resolver(ProxyResolver):

    def __init__(self, upstream, zone_file, send_request):
        super().__init__(upstream, 53, 5)
        self.zone_file = zone_file
        self.output = send_request
        self.records = self.load_zones(zone_file)

    def zone_lines(self):
        current_line = ''
        for line in self.zone_file.open():
            if line.startswith('#'):
                continue
            line = line.rstrip('\r\n\t ')
            if not line.startswith(' ') and current_line:
                yield current_line
                current_line = ''
            current_line += line.lstrip('\r\n\t ')
        if current_line:
            yield current_line

    def load_zones(self, zone_file):
        assert zone_file.exists(), f'zone files "{zone_file}" does not exist'
        self.output.emit('loading zone file "%s":' % zone_file)
        zones = []
        for line in self.zone_lines():
            try:
                rname, rtype, args_ = line.split(maxsplit=2)

                if args_.startswith('['):
                    args = tuple(json.loads(args_))
                else:
                    args = (args_,)
                record = Record(rname, rtype, args)
                zones.append(record)
                self.output.emit(' %2d: %s' % (len(zones), record))
            except Exception as e:
                raise RuntimeError(f'Error processing line ({e.__class__.__name__}: {e}) "{line.strip()}"') from e
        self.output.emit('%d zone resource records generated from zone file' % len(zones))
        return zones

    def resolve(self, request, handler):
        type_name = QTYPE[request.q.qtype]
        reply = request.reply()
        for record in self.records:
            if record.match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            self.output.emit('found zone for %s[%s], %d replies' % (request.q.qname, type_name, len(reply.rr)))
            return reply

        # no direct zone so look for an SOA record for a higher level zone
        for record in self.records:
            if record.sub_match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            self.output.emit('found higher level SOA resource for %s[%s]' % (request.q.qname, type_name))
            return reply

        self.output.emit('no local zone found, proxying %s[%s]' % (request.q.qname, type_name))
        return super().resolve(request, handler)





class DNSServerThread(QThread):
    ''' Simple DNS server UDP resolver '''
    sendRequests = pyqtSignal(object) #I'll use this object in future feature
    def __init__(self, conf):
        super(DNSServerThread, self).__init__(parent = None)
        self.resolver = None
        self.conf = conf


    def run(self):

        port = int(os.getenv('PORT', 53))
        upstream = os.getenv('UPSTREAM', '8.8.8.8')
        zone_file = Path(self.conf.get('accesspoint','path_pydns_server_zones'))
        self.resolver = Resolver(upstream, zone_file, self.sendRequests)
        self.udp_server = DNSServer(self.resolver, port=port)
        self.tcp_server = DNSServer(self.resolver, port=port, tcp=True)

        #logger.info('starting DNS server on port %d, upstream DNS server "%s"', port, upstream)
        self.udp_server.start_thread()
        self.tcp_server.start_thread()

        try:
            while self.udp_server.isAlive():
                sleep(1)
        except KeyboardInterrupt:
            pass



        # self.dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # self.dns_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.dns_sock.settimeout(0.3)  # Set timeout on socket-operations.
        # time.sleep(0.5)
        # self.dns_sock.bind(('', 53))
        # while self.DnsLoop:
        #     try:
        #         data, addr = self.dns_sock.recvfrom(1024)
        #     except:
        #         continue
        #     packet = DNSQuery(data)
        #     try:
        #         msg = dns.message.from_wire(data)
        #         op = msg.opcode()
        #         if op == 0:
        #             # standard and inverse query
        #             qs = msg.question
        #             if len(qs) > 0:
        #                 query = qs[0]
        #             #RCODE
        #     except Exception as e:
        #         query = repr(e) # error when resolver DNS
        #     self.data_request['query'] = query # get query resquest from client
        #     self.data_request['type'] = packet._get_dnsType() # get type query
        #     self.data_request['logger']='Client [{}]: -> [{}]'.format(addr[0], packet.dominio)
        #     if not self.blockResolverDNS:
        #         try:
        #             answers = self.Resolver.query(packet._get_domainReal()) # try resolver domain
        #             for rdata in answers: # get real Ipaddress
        #                 self.dns_sock.sendto(packet.render_packet(rdata.address), addr) #send resquest
        #         except dns.resolver.NXDOMAIN: # error domain not found
        #             # send domain not exist RCODE 3
        #             self.dns_sock.sendto(packet.make_response(data,3), addr)
        #         except dns.resolver.Timeout:
        #             # unable to respond query RCODE 2
        #             self.dns_sock.sendto(packet.make_response(data,2), addr) #timeout
        #         except dns.exception.DNSException:
        #             # server format ERROR unable to responde #RCODE 1
        #             self.dns_sock.sendto(packet.make_response(data,1), addr)
        #         continue
        #     # I'll use this in future for implements new feature
        #     self.dns_sock.sendto(packet.respuesta(self.GatewayAddr), addr) # for next feature
        # self.dns_sock.close()

    def stop(self):
        self.udp_server.stop()
        self.tcp_server.stop()
