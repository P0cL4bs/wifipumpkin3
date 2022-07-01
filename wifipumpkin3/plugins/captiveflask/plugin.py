from typing import Optional
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C

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


class CaptiveTemplatePlugin(object):
    Name: str = "CaptiveTemplatePlugin"
    Version: str = "1.1"
    Description: str = "Example is a simple portal default page"
    Author: str = "Pumpkin-Dev"
    TemplatePath: str  = None
    StaticPath: str = None
    Preview: str = None
    Languages: Optional[list] = []
    config: SettingsINI = SettingsINI(C.CONFIG_CP_INI)
    
    def __init__(self) -> None:
        if self.Languages:
            key = "set_{}".format(self.Name)
            if not self.config.get_all_childname(key):
                for lang in self.Languages:
                    self.config.set(key, lang, False)
                self.config.set(key, self.Languages[0], True)
        if not self.Name in self.config.get_all_childname("plugins"):
            self.config.set("plugins", self.Name, False)

    def init_language(self, lang: Optional[str]):
        if lang:
            self.TemplatePath = (
                C.TEMPLATES_FLASK + "templates/{}/templates/{}".format(self.Name, lang)
            )

    def getActivatedLanguage(self) -> Optional[str]:
        key = "set_{}".format(self.Name)
        for lang in self.config.get_all_childname(key):
            if self.config.get(key, lang, format=bool):
                return lang
        return None

    def initialize(self):
        self.init_language(self.getActivatedLanguage())
