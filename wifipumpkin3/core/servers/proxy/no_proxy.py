from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.servers.proxy.proxymode import ProxyMode

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


class NoProxy(ProxyMode):
    Name = "noproxy"
    ID = "noproxy"
    Description = "Runnning without proxy redirect traffic"
    Author = "Pumpkin-Dev"
    Hidden = True
    TypePlugin = 1
    TypeButton = 1 # 0 for Switch, 1 for Radio

    def __init__(self, parent, **kwargs):
        super(NoProxy, self).__init__(parent)
        self.setID(self.ID)
        self.setTypePlugin(self.TypePlugin)

    def boot(self):
        pass

    def parser_set_noproxy(self, status, plugin_name):
        print(display_messages("unknown sintax command", error=True))
