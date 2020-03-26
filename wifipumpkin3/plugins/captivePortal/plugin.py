import logging
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C



"""
Description:
    This program is a core for wifi-pumpkin.py. file which includes functionality
    plugins for CaptivePortal-Proxy.

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

class CaptiveTemplatePlugin(object):
	Name		= 'plugin template captive-portal'
	version		= '1.0'
	config		= SettingsINI(C.CONFIG_CP_INI)
	loggers 	= {}

	def init_language(self, lang):
		pass

	def getSellectedLanguage(self):
		selected_lang,key = None,'set_{}'.format(self.Name)
		for lang in self.config.get_all_childname(key):
			if (self.config.get_setting(key,lang, format=bool)):
				selected_lang = lang
		return selected_lang
	
	def initialize(self):
		self.init_language(self.getSellectedLanguage())
