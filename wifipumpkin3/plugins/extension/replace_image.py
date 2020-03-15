
from wifipumpkin3.plugins.extension.base import BasePumpkin
from os import path
from bs4 import BeautifulSoup
from io import StringIO

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

class replaceImages(BasePumpkin):
    meta = {
        '_name'      : 'replaceImages',
        '_version'   : '1.0',
        '_description' : 'this module proxy replace all images with the picture .',
        '_author'    : 'mh4x0f'
    }
    def __init__(self):
        for key,value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = True
        self.imagePath = self._config.get('set_replaceImages','path')

    def handleResponse(self,request, data):
        self.content = request.responseHeaders.getRawHeaders('content-type')
        if str(self.content).startswith('image'):
            if path.isfile(self.imagePath):
                try:
                    img = StringIO(open(self.imagePath, 'rb').read().decode())
                    data = img.getvalue()
                    print('[{}] URL:{} image replaced...'.format(self._name,request.uri))
                except:
                    pass
        return data