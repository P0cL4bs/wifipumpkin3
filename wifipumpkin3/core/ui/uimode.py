import urwid


class WidgetBase(urwid.ListBox):
    """
    common class for widgets
    """

    def __init__(self, ui, *args, **kwargs):
        self.ui = ui
        super().__init__(*args, **kwargs)
        self.ro_content = self.body[:]  
        self.body_change_lock = threading.Lock()

    def set_body(self, widgets):
        with self.body_change_lock:
            self.body[:] = widgets

    def reload_widget(self):
        with self.body_change_lock:
            self.body[:] = self.body