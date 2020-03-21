import urwid
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
import threading

class WidgetBase(urwid.Frame):
    """
    common class for widgets
    """
    _conf = SettingsINI(C.CONFIG_INI)

    def __init__(self, ui, *args, **kwargs):
        self.ui = ui
        super().__init__(*args, **kwargs)
        self.ro_content = self.body[:]  
        self.body_change_lock = threading.Lock()

    def setup_view(self):
        raise NotImplementedError

    def main(self):
        raise NotImplementedError

    def handleWindow(self, key):
        raise NotImplementedError

    def render_view(self):
        return self

    def set_body(self, widgets):
        with self.body_change_lock:
            self.body = widgets

    def set_header(self, widgets):
        with self.body_change_lock:
            self.header = widgets  

    def set_footer(self, widgets):
        with self.body_change_lock:
            self.footer = widgets       

    def reload_widget(self):
        with self.body_change_lock:
            self.body[:] = self.body