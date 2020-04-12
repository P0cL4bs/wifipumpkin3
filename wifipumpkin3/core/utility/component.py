from wifipumpkin3.core.config.globalimport import *

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


class ComponentBlueprint(object):
    Name = "GenericComponent"
    ID = "Generic"

    def __init__(self):
        super(ComponentBlueprint, self).__init__()
        self.reactor = None
        self.service = None

    def Initialize(self):
        """
        Initialise everything here
        :return:
        """
        pass

    def boot(self):
        """
        Thing you will need to do aftere initialization here
        :return:
        """
        pass

    def postBoot(self):
        """
        Things you do after boot here
        :return:
        """
        pass

    def shutdown(self):
        pass

    def LogOutput(self, data):
        print(data)

    def Start(self):
        self.PreBoot()
        self.Initialize()
        self.boot()
        self.PostBoot()

    def Stop(self):
        pass

    @property
    def Settings(self):
        pass

    def stupidthings(self):
        print("From Component Blueprint")

    def PreBoot(self):
        pass

    def PostBoot(self):
        pass


class ControllerBlueprint(object):
    Name = "GenericController"
    ID = "Generic"

    def __init__(self):
        super(ControllerBlueprint, self).__init__()

    @staticmethod
    def getID():
        """
        Initialise everything here
        :return ID:
        """
        return ComponentBlueprint.ID

    @property
    def Active(self):
        pass

    @property
    def ActiveReactor(self):
        pass

    @property
    def ActiveService(self):
        pass

    def Start(self):
        pass

    def Stop(self):
        pass

    def SaveLog(self):
        pass

    def LogOutput(self, data):
        pass
