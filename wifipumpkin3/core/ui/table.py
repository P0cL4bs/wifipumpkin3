import urwid,time,threading
from tabulate import tabulate
from netaddr import EUI
from wifipumpkin3.core.utility.collection import SettingsINI
import wifipumpkin3.core.utility.constants as C
from beautifultable import BeautifulTable
import fcntl, termios, struct, os
from wifipumpkin3.core.common.platforms import hexdump
from multiprocessing import Process
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.ui.uimode import WidgetBase

palette_color = [
    ('titlebar', 'black,bold', 'yellow'),
    ('refresh button', 'dark green,bold', 'black'),
    ('quit button', 'dark red,bold', 'black'),
    ('getting quote', 'dark blue', 'black'),
    ('getting quote', 'dark blue', ''),
    ('headers', 'white,bold', ''),
    ('change', 'dark green', ''),
    ('change negative', 'dark red', ''),
    ('body', 'white', 'black'),
    ('title', 'black,bold', 'yellow'),
]

class TableWidget(BeautifulTable):
    def __int__(self):
        BeautifulTable.__init__(self)

    def createColumn(self):
        self.column_headers = ['URL', 'Method', 'Track']
        self.column_alignments['URL'] = BeautifulTable.ALIGN_LEFT
        self.column_alignments['Track'] = BeautifulTable.ALIGN_LEFT

    def setup(self):
        self.createColumn()
        self.left_border_char = ''
        self.right_border_char = ''
        self.top_border_char = ''
        self.bottom_border_char = ''
        self.header_seperator_char = '-'
        self.row_seperator_char = ''
       # self.intersection_char = ''
        self.column_seperator_char = '|'

    def get_sizeobject(self):
        return self.__len__()

    def get_table_string(self):
        return self.__str__()

    def upSizeTerminal(self):
        self._max_table_width = self._getTerminalSize_linux()[0] - 2

    def _getTerminalSize_linux(self):
        """ getTerminalSize()
         - get width and height of console
         - works on linux,os x,windows,cygwin(windows)
         originally retrieved from:
         http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
        """
        def ioctl_GWINSZ(fd):
            try:
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
            except:
                return None
            return cr
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            try:
                cr = (env['LINES'], env['COLUMNS'])
            except:
                return None
        return int(cr[1]), int(cr[0])

class ui_TableMonitorClient(WidgetBase):
    ConfigRoot = "ui_table_mod"
    SubConfig = "ui_table_mod"
    ID = "ui_table_mod"
    Name = "ui_table_mod"


    def __init__(self, parent):
        self.parent = parent
        self.table_clients = []
        self.__threadServices = []
        self.__threadStatus = False
        self.header_text = [
            ('titlebar', ''), 'Clients: ',('titlebar','     '),
            ('title', 'UP'), ',', ('title', 'DOWN'), ':scroll',
            '     Monitor DHCP Requests',
        ]

    def getClientsCount(self):
        return len(self.table_clients)

    def setup_view(self):
        self.header_wid = urwid.AttrWrap(urwid.Text(self.header_text), 'title')
        self.menu = urwid.Text([u'Press (', ('quit button', u'Q'), u') to quit.'])
        self.lwDevices = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.lwDevices)
        self.main_box = urwid.LineBox(self.body)

        self.layout = urwid.Frame(header=self.header_wid, body=self.main_box, footer=self.menu)
        self.add_Clients(Refactor.readFileDataToJson(C.CLIENTS_CONNECTED))

    def render_view(self):
        return self.layout

    def main(self):
        self.setup_view()
        loop = urwid.MainLoop(
            self.render_view(), palette=palette_color,
            unhandled_input=self.handleWindow)
        loop.set_alarm_in(1, self.refresh)
        loop.run()

    def refresh(self, loop=None, data=None):
        self.setup_view()
        loop.widget = self.render_view()
        loop.set_alarm_in(1, self.refresh)

    def start(self):
        self.main()

    def stop(self):
        if len(self.__threadServices) > 0:
            self.table_clients = []
            self.lwDevices.append(urwid.Text(('', self.up_Clients())))

    def get_mac_vendor(self,mac):
        ''' discovery mac vendor by mac address '''
        try:
            d_vendor = EUI(mac)
            d_vendor = d_vendor.oui.registration().org
        except:
            d_vendor = 'unknown vendor'
        return d_vendor

    def add_Clients(self, data_dict):
        ''' add client on table list() '''
        self.table_clients = []
        for data in data_dict:
            self.table_clients.append([data_dict[data]['HOSTNAME'],
            data_dict[data]['IP'],data_dict[data]['MAC'],
            self.get_mac_vendor(data_dict[data]['MAC'])])
            self.lwDevices.clear()
            self.lwDevices.append(urwid.Text(('', self.up_Clients())))
            self._body.set_focus(len(self.lwDevices) - 1, 'above')

    def up_Clients(self):
        if len(self.table_clients) > 0:
            return tabulate(self.table_clients,('Hostname','IP','Mac','Vendor'))
        return ''

    def handleWindow(self, key):
        if key == 'R' or key == 'r':
            pass
        elif key == 'Q' or key == 'q' or key  == 'esc':
            raise urwid.ExitMainLoop()