
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C

class BasePumpkin(object):
    _name    = 'plugin base PumpkinProxy '
    _version = '1.0'
    _config  = SettingsINI(C.CONFIG_TP_INI)

    @staticmethod
    def getName():
        return BasePumpkin._name
        
    def handleHeader(self, request, key, value):
        raise NotImplementedError

    def handleResponse(self, request, data):
        raise NotImplementedError