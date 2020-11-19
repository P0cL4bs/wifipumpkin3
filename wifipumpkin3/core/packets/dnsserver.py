from PyQt5.QtCore import QThread, pyqtSignal, QThread
import json
import os
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from time import sleep
import wifipumpkin3.core.utility.constants as C
from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer
from wifipumpkin3.core.utility.printer import display_messages

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

TYPE_LOOKUP = {
    "A": (dns.A, QTYPE.A),
    "AAAA": (dns.AAAA, QTYPE.AAAA),
    "CAA": (dns.CAA, QTYPE.CAA),
    "CNAME": (dns.CNAME, QTYPE.CNAME),
    "DNSKEY": (dns.DNSKEY, QTYPE.DNSKEY),
    "MX": (dns.MX, QTYPE.MX),
    "NAPTR": (dns.NAPTR, QTYPE.NAPTR),
    "NS": (dns.NS, QTYPE.NS),
    "PTR": (dns.PTR, QTYPE.PTR),
    "RRSIG": (dns.RRSIG, QTYPE.RRSIG),
    "SOA": (dns.SOA, QTYPE.SOA),
    "SRV": (dns.SRV, QTYPE.SRV),
    "TXT": (dns.TXT, QTYPE.TXT),
    "SPF": (dns.TXT, QTYPE.TXT),
}

SERIAL_NO = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())


class Record:
    def __init__(self, rname, rtype, args):
        self._rname = DNSLabel(rname)

        rd_cls, self._rtype = TYPE_LOOKUP[rtype]

        if self._rtype == QTYPE.SOA and len(args) == 2:
            # add sensible times to SOA
            args += ((SERIAL_NO, 3600, 3600 * 3, 3600 * 24, 3600),)

        if (
            self._rtype == QTYPE.TXT
            and len(args) == 1
            and isinstance(args[0], str)
            and len(args[0]) > 255
        ):
            # wrap long TXT records as per dnslib's docs.
            args = (wrap(args[0], 255),)

        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            ttl = 3600 * 24
        else:
            ttl = 300

        self.rr = RR(
            rname=self._rname, rtype=self._rtype, rdata=rd_cls(*args), ttl=ttl,
        )

    def match(self, q):
        return q.qname == self._rname and (
            q.qtype == QTYPE.ANY or q.qtype == self._rtype
        )

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
        current_line = ""
        for line in self.zone_file.open():
            if line.startswith("#"):
                continue
            line = line.rstrip("\r\n\t ")
            if not line.startswith(" ") and current_line:
                yield current_line
                current_line = ""
            current_line += line.lstrip("\r\n\t ")
        if current_line:
            yield current_line

    def load_zones(self, zone_file):
        assert zone_file.exists(), f'zone files "{zone_file}" does not exist'
        self.output.emit('loading zone file "%s":' % zone_file)
        zones = []
        for line in self.zone_lines():
            try:
                rname, rtype, args_ = line.split(maxsplit=2)

                if args_.startswith("["):
                    args = tuple(json.loads(args_))
                else:
                    args = (args_,)
                record = Record(rname, rtype, args)
                zones.append(record)
                self.output.emit(" %2d: %s" % (len(zones), record))
            except Exception as e:
                raise RuntimeError(
                    f'Error processing line ({e.__class__.__name__}: {e}) "{line.strip()}"'
                ) from e
        self.output.emit(
            "%d zone resource records generated from zone file" % len(zones)
        )
        return zones

    def resolve(self, request, handler):
        type_name = QTYPE[request.q.qtype]
        reply = request.reply()
        for record in self.records:
            if record.match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            self.output.emit(
                "found zone for %s[%s], %d replies"
                % (request.q.qname, type_name, len(reply.rr))
            )
            return reply

        # no direct zone so look for an SOA record for a higher level zone
        for record in self.records:
            if record.sub_match(request.q):
                reply.add_answer(record.rr)

        if reply.rr:
            self.output.emit(
                "found higher level SOA resource for %s[%s]"
                % (request.q.qname, type_name)
            )
            return reply

        self.output.emit(
            "no local zone found, proxying %s[%s]" % (request.q.qname, type_name)
        )
        return super().resolve(request, handler)


class LocalDNSLogger(object):

    """
        The class provides a default set of logging functions for the various
        stages of the request handled by a DNSServer instance which are
        enabled/disabled by flags in the 'log' class variable.
        To customise logging create an object which implements the LocalDNSLogger
        interface and pass instance to DNSServer.
        The methods which the logger instance must implement are:
            log_recv          - Raw packet received
            log_send          - Raw packet sent
            log_request       - DNS Request
            log_reply         - DNS Response
            log_truncated     - Truncated
            log_error         - Decoding error
            log_data          - Dump full request/response
    """

    def __init__(self, logger):
        self.logger = logger

    def log_recv(self, handler, data):
        pass
        # self.logger.emit("Received: [%s:%d] (%s) <%d> : %s" %(
        #              handler.client_address[0],
        #              handler.client_address[1],
        #              handler.protocol,
        #              len(data),
        #              binascii.hexlify(data)))

    def log_send(self, handler, data):
        pass
        # self.logger.emit("Sent: [%s:%d] (%s) <%d> : %s" %(
        #              handler.client_address[0],
        #              handler.client_address[1],
        #              handler.protocol,
        #              len(data),
        #              binascii.hexlify(data)))

    def log_request(self, handler, request):
        pass
        # self.logger.emit("Request: [%s:%d] (%s) / '%s' (%s)" %(
        #              handler.client_address[0],
        #              handler.client_address[1],
        #              handler.protocol,
        #              request.q.qname,
        #              QTYPE[request.q.qtype]))
        # self.log_data(request)

    def log_reply(self, handler, reply):
        pass
        # self.logger.emit("Reply: [%s:%d] (%s) / '%s' (%s) / RRs: %s" %(
        #              handler.client_address[0],
        #              handler.client_address[1],
        #              handler.protocol,
        #              reply.q.qname,
        #              QTYPE[reply.q.qtype],
        #              ",".join([QTYPE[a.rtype] for a in reply.rr])))
        # self.log_data(reply)

    def log_truncated(self, handler, reply):
        pass
        # self.logger.emit("Truncated Reply: [%s:%d] (%s) / '%s' (%s) / RRs: %s" %(
        #              handler.client_address[0],
        #              handler.client_address[1],
        #              handler.protocol,
        #              reply.q.qname,
        #              QTYPE[reply.q.qtype],
        #              ",".join([QTYPE[a.rtype] for a in reply.rr])))
        # self.log_data(reply)

    def log_error(self, handler, e):
        pass
        # self.logger.emit("Invalid Request: [%s:%d] (%s) :: %s" %(
        #              handler.client_address[0],
        #              handler.client_address[1],
        #              handler.protocol,
        #              e))

    def log_data(self, dnsobj):
        self.logger.emit("\n" + dnsobj.toZone("    ") + "\n")


class DNSServerThread(QThread):
    """ Simple DNS server UDP resolver """

    sendRequests = pyqtSignal(object)  # I'll use this object in future feature

    def __init__(self, conf):
        super(DNSServerThread, self).__init__(parent=None)
        self.resolver = None
        self.conf = conf

    def run(self):

        port = int(os.getenv("PORT", 53))
        upstream = os.getenv("UPSTREAM", "8.8.8.8")
        zone_file = Path(C.DNSHOSTS)
        self.logger_dns = LocalDNSLogger(self.sendRequests)
        self.resolver = Resolver(upstream, zone_file, self.sendRequests)
        self.udp_server = DNSServer(self.resolver, port=port, logger=self.logger_dns)
        self.tcp_server = DNSServer(
            self.resolver, port=port, logger=self.logger_dns, tcp=True
        )
        print(display_messages("starting {}".format(self.objectName()), info=True))

        # logger.info('starting DNS server on port %d, upstream DNS server "%s"', port, upstream)
        self.udp_server.start_thread()
        self.tcp_server.start_thread()

        try:
            while self.udp_server.isAlive():
                sleep(1)
        except KeyboardInterrupt:
            pass

    def getpid(self):
        """ return the pid of current process in background"""
        return "thread"

    def getID(self):
        """ return the name of process in background"""
        return self.objectName()

    def stop(self):
        self.udp_server.stop()
        self.tcp_server.stop()
        print(
            display_messages(
                "thread {} successfully stopped".format(self.objectName()), info=True
            )
        )
