import urwid,time,threading
from tabulate import tabulate
from netaddr import EUI
from core.utility.collection import SettingsINI
import core.utility.constants as C
from beautifultable import BeautifulTable
import fcntl, termios, struct, os
from core.common.platforms import hexdump
from multiprocessing import Process

palette = [
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
        self.intersection_char = ''
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


class ui_MonitorSniffer(object):
    palette = [
        ('body', 'white', ''),
        ('ext', 'white', 'dark blue'),
        ('ext_hi', 'light cyan', 'dark blue', 'bold'),
        ('line_url', 'light cyan', ''),
        ]

    header_text = [
        ('ext_hi', 'ESC'), ':quit        ',
        ('ext_hi', 'UP'), ',', ('ext_hi', 'DOWN'), ':scroll',
        ]
    def __init__(self, parent):
        self.parent = parent
        self.conf  = SettingsINI(C.TCPPROXY_INI)
        self.list_url_monitor = []
        self.listThread = []
        self.table_url_monitor = TableWidget()
        self.table_url_monitor.setup()
        self.thread_status = False
        self.create_ui()


    def setupThreads(self):
        if (not self.thread_status):
            t1 = threading.Thread(target= self.parent.sniffs.tcp_proxy.get_output_activated)
            t2 = threading.Thread(target=self.monitor_queue_tcpproxy)
            self.listThread.append(t1)
            self.listThread.append(t2)
            self.thread_status = True
            for thread in self.listThread:
                thread.daemon = True
                thread.start()

    def create_ui(self):
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'ext')
        self.flowWalker = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.flowWalker)
        self.flowWalker2 = urwid.SimpleListWalker([])
        self.body2 = urwid.ListBox(self.flowWalker2)



        self.flowWalker3 = urwid.SimpleListWalker([])
        self.body3 = urwid.ListBox(self.flowWalker3)

        self.footer = urwid.AttrWrap(urwid.Edit('Edit:  '), 'ext')

        self.main_box = urwid.LineBox(self.body)
        self.main_box.set_title('URL Capture')
        self.main_box2 = urwid.LineBox(self.body2)
        self.main_box2.set_title('Dump POST')

        self.main_box3 = urwid.LineBox(self.body3)
        self.main_box3.set_title('Pumpkin Proxy')
        
        self.columns = urwid.Columns([self.main_box], dividechars=1)
        self.columns2 = urwid.Columns([self.main_box2,self.main_box3], dividechars=1)
        self.main_layout = urwid.Pile([
            self.columns,
            self.columns2
        ])
        self.view = urwid.Frame(
            urwid.AttrWrap(self.main_layout, 'body'),
            header = self.header,
            footer = self.footer)

        self.main_loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input = self.unhandled_input)
        self.monitor_loop(self.main_loop, None)

    def unhandled_input(self, k):
        if k == 'esc':
            raise urwid.ExitMainLoop()

    def monitor_loop(self, loop, *args):
        loop.set_alarm_in(sec=0.5,callback=self.monitor_loop)

    def up_urlmonitor(self):
        self.table_url_monitor.upSizeTerminal()
        if self.table_url_monitor.get_sizeobject() > 0:
            return list(self.table_url_monitor.get_table_string().split('\n'))
        return ''

    def append_parserData3(self, data):
        self.flowWalker3.append(urwid.Text(('', 'Username: {}'.format(data))))


    def append_parserData(self, data):
        if list(dict(data).keys())[0] == 'urlsCap' :
            url = '{}{}'.format(data['urlsCap']['Headers']['Host'].decode('utf-8'),
                                data['urlsCap']['Headers']['Path'].decode('utf-8'))
            if len(url) > 65:
                url = url[:65]+'...'
            self.table_url_monitor.append_row([url,
                data['urlsCap']['Headers']['Method'].decode('utf-8'),
                '[ {0[src]} ]'.format(data['urlsCap']['IP']),])
            self.flowWalker.clear()
            for line in self.up_urlmonitor():
                self.flowWalker.append(urwid.Text(('', line)))
            self.body.set_focus(len(self.flowWalker) - 1, 'above')
        elif list(dict(data).keys())[0] == 'POSTCreds' :
            self.flowWalker2.append(urwid.Text([('', '['), ('line_url', 'Headers'), ('', "]") ]))
            #for name, valur in data['POSTCreds']['User'].iteritems():
            #    self.send_output.emit('{}: {}'.format(name, valur))

            for key, value in iter(data['POSTCreds']['Packets']['Headers'].items()):
                if key != 'Headers':
                    self.flowWalker2.append(urwid.Text(('', '{:>20} : {}'.format(key,str(value,'utf-8')))))
            #print(data['POSTCreds']['Packets'])
            self.flowWalker2.append(urwid.Text([('', '['), ('line_url', 'Body'), ('', "]")]))
            self.flowWalker2.append(urwid.Text(('', '{}'.format(hexdump(data['POSTCreds']['Payload'])))))

            self.flowWalker2.append(urwid.Text([('', '['), ('line_url', 'Credentials'), ('', "]")]))
            self.flowWalker2.append(urwid.Text(('', 'Username: {}'.format(data['POSTCreds']['User']))))
            self.flowWalker2.append(urwid.Text(('', 'Password: {}'.format(data['POSTCreds']['Pass']))))
            self.flowWalker2.append(urwid.Text(('', 'Packets: {}'.format(data['POSTCreds']['Destination']))))

    def monitor_queue_tcpproxy(self):
        while self.thread_status:
            if self.parent.sniffs.tcp_proxy.msg_output:
                self.append_parserData(self.parent.sniffs.tcp_proxy.msg_output.pop(0))

            if self.parent.sniffs.Thread_PumpkinProxy.send:
                self.append_parserData3(self.parent.sniffs.Thread_PumpkinProxy.send.pop(0))


    def start(self):
        self.main_loop.run()

    def stop(self):
        self.listThread = []
        self.thread_status = False



class ui_TableMonitorClient(object):
    def __init__(self, parent):
        self.parent = parent
        self.conf = SettingsINI(C.CONFIG_INI)
        self.table_clients = []
        self.threadsMonitor = []
        self.thread_status = False
        self.header_text = [
            ('titlebar', ''), 'Clients: ',('titlebar','     '),
            ('title', 'UP'), ',', ('title', 'DOWN'), ':scroll',
            '     Monitor DHCPServer Requests',
        ]
        self.create_ui()

    def getClientsCount(self):
        return len(self.table_clients)

    def setupThreads(self):
        if (not self.thread_status):
            t1 = threading.Thread(target= self.monitor_queue_message)
            t2 = threading.Thread(target= self.parent.ac.threadDHCP.DHCPProtocol.get_DHCPServerResponse)
            t3 = threading.Thread(target= self.parent.ac.Thread_hostapd.getHostapdResponse)
            self.threadsMonitor.append(t1)
            self.threadsMonitor.append(t2)
            self.threadsMonitor.append(t3)
            self.thread_status = True
            for thread in self.threadsMonitor:
                thread.daemon = True
                thread.start()

    def create_ui(self):
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'title')
        self.menu = urwid.Text([
            u'Press (', ('refresh button', u'R'), u') to get a new client. ',
            u'Press (', ('quit button', u'Q'), u') to quit.'])
        self.listWalker = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.listWalker)
        self.main_box = urwid.LineBox(self.body)

        self.layout = urwid.Frame(header=self.header, body=self.main_box, footer=self.menu)
        self.main_loop = urwid.MainLoop(self.layout, palette, unhandled_input=self.handle_input)
        self.monitor_loop(self.main_loop, None)


    def monitor_loop(self, loop, *args):
        loop.set_alarm_in(sec=0.5,callback=self.monitor_loop)

    def monitor_queue_message(self):
        while self.thread_status:
            if self.parent.ac.threadDHCP.DHCPProtocol.message:
                self.add_Clients(self.parent.ac.threadDHCP.DHCPProtocol.message.pop(0))
            if self.parent.ac.Thread_hostapd.msg_inactivity:
                self.rm_ClientsTable(self.parent.ac.Thread_hostapd.msg_inactivity.pop(0))


    def start(self):
        # if self.conf.get('accesspoint','statusAP',format=bool):
        #     if (not self.thread_status):
        #         t1 = threading.Thread(target= self.monitor_queue_message)
        #         t2 = threading.Thread(target= self.parent.ac.threadDHCP.DHCPProtocol.get_DHCPServerResponse)
        #         t3 = threading.Thread(target= self.parent.ac.Thread_hostapd.getHostapdResponse)
        #         self.threadsMonitor.append(t1)
        #         self.threadsMonitor.append(t2)
        #         self.threadsMonitor.append(t3)
        #         self.thread_status = True
        #         for thread in self.threadsMonitor:
        #             thread.daemon = True
        #             thread.start()
        #self.add_Clients({'HOSTNAME': 'android-teste-login', 'IP': '10.0.0.1', 'MAC': 'BC:F6:85:03:36:5B'})
        self.main_loop.run()

    def stop(self):
        if len(self.threadsMonitor) > 0:
            self.table_clients = []
            self.listWalker.append(urwid.Text(('', self.up_Clients())))
        self.threadsMonitor = []

    def get_mac_vendor(self,mac):
        ''' discovery mac vendor by mac address '''
        try:
            d_vendor = EUI(mac)
            d_vendor = d_vendor.oui.registration().org
        except:
            d_vendor = 'unknown vendor'
        return d_vendor

    def add_Clients(self, data):
        ''' add client on table list() '''
        if self.table_clients  != []:
            for (host, ip, mac, vendor) in self.table_clients:
                if (mac == data['MAC']):
                    return
        self.table_clients.append([data['HOSTNAME'],data['IP'],data['MAC'],self.get_mac_vendor(data['MAC'])])
        self.listWalker.clear()
        self.listWalker.append(urwid.Text(('', self.up_Clients())))
        self.body.set_focus(len(self.listWalker) - 1, 'above')

    def rm_ClientsTable(self, data):
        ''' remove client from table '''
        if self.table_clients  != []:
            for (host, ip, mac, vendor) in self.table_clients:
                if (mac == data):
                    self.table_clients.remove([host, ip, mac, vendor])
                    break
        self.listWalker.clear()
        self.listWalker.append(urwid.Text(('', self.up_Clients())))

    def up_Clients(self):
        if len(self.table_clients) > 0:
            return tabulate(self.table_clients,('Hostname','IpAddr','MacAddr','Vendor'))
        return ''

    def handle_input(self, key):
        if key == 'R' or key == 'r':
            self.main_loop.draw_screen()
            self.listWalker.clear()
            self.listWalker.append(urwid.Text(('', self.up_Clients())))
        elif key == 'Q' or key == 'q' or key  == 'esc':
            raise urwid.ExitMainLoop()
