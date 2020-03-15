from wifipumpkin3.plugins.extension.base import BasePumpkin

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


class nocache(BasePumpkin):
    meta = {
        '_name': 'no-cache',
        '_version': '1.0',
        '_description': 'disable browser caching, cache-control in HTML',
        '_author': 'mh4x0f'
    }

    def __init__(self):
        for key, value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = False

    def handleHeader(self, request, key, value):
        if (key.decode().lower() == 'cache-control'):
            value = 'no-cache'.encode()

        if (key.decode().lower() == 'if-none-match'):
            value = ''.encode()
        if (key.decode().lower() == 'etag'):
            value = ''.encode()
