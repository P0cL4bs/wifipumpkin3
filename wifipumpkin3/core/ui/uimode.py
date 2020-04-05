import urwid
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
import threading

class WidgetBase(urwid.Frame):
    """
    common class for widgets
    """
    _conf = SettingsINI(C.CONFIG_INI)

    def __init__(self, *args, **kwargs):
        pass

    def setup_view(self):
        raise NotImplementedError

    def main(self):
        raise NotImplementedError

    def handleWindow(self, key):
        raise NotImplementedError

    def render_view(self):
        return self