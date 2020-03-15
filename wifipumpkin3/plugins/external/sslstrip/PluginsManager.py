import inspect

class PluginsManager:

    _plugins = {}
    _instance = None

    @property
    def plugins(self):
        return self._plugins

    @plugins.setter
    def plugins(self, p):
        self._plugins[p.getName()] = p()

    def addPlugin(self, p):
        self.plugins = p

    @staticmethod
    def getInstance():
        if PluginsManager._instance == None:
            PluginsManager._instance = PluginsManager()
        return PluginsManager._instance

    def hook(self, plugin, attr, request, *args):
        return getattr(self.plugins[plugin], attr['function'])(request, *args)
        