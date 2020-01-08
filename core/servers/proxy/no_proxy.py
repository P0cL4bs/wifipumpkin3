from core.common.uimodel import *
from core.servers.proxy.proxymode import ProxyMode

class NoProxy(ProxyMode):
    Name="noproxy"
    Author = "Pumpkin-Dev"
    Hidden = True
    TypePlugin = 1

    def __init__(self, parent, **kwargs):
        super(NoProxy, self).__init__(parent)
        self.setID(self.Name)
        self.setTypePlugin(self.TypePlugin)

        # self.controlui.setChecked(self.FSettings.Settings.get_setting('plugins', self.Name, format=bool))
        # self.controlui.toggled.connect(self.CheckOptions)
        #self.setEnabled(self.FSettings.Settings.get_setting('plugins', self.Name, format=bool))
        #parent.PopUpPlugins.GroupPluginsProxy.setChecked(not self.FSettings.Settings.get_setting('plugins', self.Name, format=bool))

    def boot(self):
        pass