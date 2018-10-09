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
        self.conf  = SettingsINI(C.CONFIG_TP_INI)
        self.tbUrlMonitor = TableWidget()
        self.tbUrlMonitor.setup()
        self.__threadServices = []
        self.__threadStatus = False
        self.create_ui()

    def getThreadStatus(self):
        if self.__threadStatus:
            return True
        return False

    def getThreadList(self):
        return self.__threadServices
    
    def setThreadStatus(self, status):
        self.__threadStatus = status

    def appendThreads(self, threads=list):
        for thread in threads:
            self.__threadServices.append(thread)

    def startThreads(self):
        if (not self.getThreadStatus()):
            t1 = threading.Thread(target= self.parent.sniffs.tcp_proxy.get_output_activated)
            t2 = threading.Thread(target=self.threadsQueueProxy)
            self.appendThreads([t1, t2])
            self.setThreadStatus(True)
            for thread in self.getThreadList():
                thread.daemon = True
                thread.start()

    def create_ui(self):
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'ext')
        self.footer = urwid.AttrWrap(urwid.Edit('Edit:  '), 'ext')

        self.swl_urlMonitor = urwid.SimpleListWalker([])
        self.swl_creds = urwid.SimpleListWalker([])
        self.swl_kinProxy = urwid.SimpleListWalker([])

        self.lbUrlMonitor = urwid.ListBox(self.swl_urlMonitor)
        self.lbCredsMonitor = urwid.ListBox(self.swl_creds)
        self.lbPumpkinProxy = urwid.ListBox(self.swl_kinProxy)

        self.boxUrlMonitor = urwid.LineBox(self.lbUrlMonitor)
        self.boxCredsMonitor = urwid.LineBox(self.lbCredsMonitor)
        self.boxPumpkinProxy = urwid.LineBox(self.lbPumpkinProxy)

        self.boxUrlMonitor.set_title('URL Capture')
        self.boxCredsMonitor.set_title('Dump POST')
        self.boxPumpkinProxy.set_title('Pumpkin Proxy')
        
        self.columnsUrl = urwid.Columns([self.boxUrlMonitor], dividechars=1)
        self.colummnsPayload = urwid.Columns([self.boxCredsMonitor,self.boxPumpkinProxy], dividechars=1)
        self.main_layout = urwid.Pile([
            self.columnsUrl,
            self.colummnsPayload
        ])

        self.view = urwid.Frame(urwid.AttrWrap(self.main_layout, 'body'),
            header = self.header,footer = self.footer)

        self.main_loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input = self.unhandledOutput)
        self.monitor_loop(self.main_loop, None)

    def unhandledOutput(self, k):
        if k == 'esc':
            raise urwid.ExitMainLoop()

    def monitor_loop(self, loop, *args):
        loop.set_alarm_in(sec=0.3,callback=self.monitor_loop)

    def up_urlmonitor(self):
        self.tbUrlMonitor.upSizeTerminal()
        if self.tbUrlMonitor.get_sizeobject() > 0:
            return list(self.tbUrlMonitor.get_table_string().split('\n'))
        return ''

    def append_parserDataProxy(self, data):
        self.swl_kinProxy.append(urwid.Text(('', 'Username: {}'.format(data))))

    def append_parserData(self, data):
        if list(dict(data).keys())[0] == 'urlsCap' :
            url = '{}{}'.format(data['urlsCap']['Headers']['Host'].decode('utf-8'),
                                data['urlsCap']['Headers']['Path'].decode('utf-8'))

            if len(url) > 65: url = url[:65]+'...'

            self.tbUrlMonitor.append_row([url,data['urlsCap']['Headers']['Method'].decode('utf-8'),
                '[ {0[src]} ]'.format(data['urlsCap']['IP']),])
            self.swl_urlMonitor.clear()
            for line in self.up_urlmonitor():
                self.swl_urlMonitor.append(urwid.Text(('', line)))
            self.lbUrlMonitor.set_focus(len(self.swl_urlMonitor) - 1, 'above')

        elif list(dict(data).keys())[0] == 'POSTCreds' :

            self.swl_creds.append(urwid.Text([('', '['), ('line_url', 'Headers'), ('', "]") ]))
            for key, value in iter(data['POSTCreds']['Packets']['Headers'].items()):
                if key != 'Headers':
                    self.swl_creds.append(urwid.Text(('', '{:>20} : {}'.format(key,str(value,'utf-8')))))

            self.swl_creds.append(urwid.Text([('', '['), ('line_url', 'Body'), ('', "]")]))
            self.swl_creds.append(urwid.Text(('', '{}'.format(hexdump(data['POSTCreds']['Payload'])))))
            self.swl_creds.append(urwid.Text([('', '['), ('line_url', 'Credentials'), ('', "]")]))
            self.swl_creds.append(urwid.Text(('', 'Username: {}'.format(data['POSTCreds']['User']))))
            self.swl_creds.append(urwid.Text(('', 'Password: {}'.format(data['POSTCreds']['Pass']))))
            self.swl_creds.append(urwid.Text(('', 'Packets: {}'.format(data['POSTCreds']['Destination']))))
            self.lbCredsMonitor.set_focus(len(self.swl_creds) - 1, 'above')

    def threadsQueueProxy(self):
        while self.getThreadStatus():
            if self.parent.sniffs.tcp_proxy.msg_output:
                self.append_parserData(self.parent.sniffs.tcp_proxy.msg_output.pop(0))

            if self.parent.sniffs.Thread_PumpkinProxy.send:
                self.append_parserDataProxy(self.parent.sniffs.Thread_PumpkinProxy.send.pop(0))

    def start(self):
        self.main_loop.run()

    def stop(self):
        self.__threadServices = []
        self.setThreadStatus(False)



class ui_TableMonitorClient(object):
    def __init__(self, parent):
        self.parent = parent
        self.conf = SettingsINI(C.CONFIG_INI)
        self.table_clients = []
        self.__threadServices = []
        self.__threadStatus = False
        self.header_text = [
            ('titlebar', ''), 'Clients: ',('titlebar','     '),
            ('title', 'UP'), ',', ('title', 'DOWN'), ':scroll',
            '     Monitor DHCPServer Requests',
        ]
        self.create_ui()


    def getThreadStatus(self):
        if self.__threadStatus:
            return True
        return False
    

    def getThreadList(self):
        return self.__threadServices

    def setThreadStatus(self, status):
        self.__threadStatus = status

    def getClientsCount(self):
        return len(self.table_clients)

    def appendThreads(self, threads=list):
        for thread in threads:
            self.__threadServices.append(thread)

    def startThreads(self):
        if (not self.getThreadStatus()):
            t1 = threading.Thread(target= self.monitor_queue_message)
            t2 = threading.Thread(target= self.parent.ac.threadDHCP.DHCPProtocol.get_DHCPServerResponse)
            t3 = threading.Thread(target= self.parent.ac.Thread_hostapd.getHostapdResponse)
            self.appendThreads([t1,t2,t3])
            self.setThreadStatus(True)
            for thread in self.getThreadList():
                thread.daemon = True
                thread.start()

    def create_ui(self):
        self.header = urwid.AttrWrap(urwid.Text(self.header_text), 'title')
        self.menu = urwid.Text([
            u'Press (', ('refresh button', u'R'), u') to get a new client. ',
            u'Press (', ('quit button', u'Q'), u') to quit.'])
        self.lwDevices = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.lwDevices)
        self.main_box = urwid.LineBox(self.body)

        self.layout = urwid.Frame(header=self.header, body=self.main_box, footer=self.menu)
        self.main_loop = urwid.MainLoop(self.layout, palette, unhandled_input=self.handleWindow)
        self.monitor_loop(self.main_loop, None)

    def monitor_loop(self, loop, *args):
        loop.set_alarm_in(sec=0.3,callback=self.monitor_loop)

    def monitor_queue_message(self):
        while self.getThreadStatus():
            if self.parent.ac.threadDHCP.DHCPProtocol.message:
                self.add_Clients(self.parent.ac.threadDHCP.DHCPProtocol.message.pop(0))
            if self.parent.ac.Thread_hostapd.msg_inactivity:
                self.rm_ClientsTable(self.parent.ac.Thread_hostapd.msg_inactivity.pop(0))

    def start(self):
        self.main_loop.run()

    def stop(self):
        if len(self.__threadServices) > 0:
            self.table_clients = []
            self.lwDevices.append(urwid.Text(('', self.up_Clients())))
        self.__threadServices = []
        self.setThreadStatus(False)

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
        self.lwDevices.clear()
        self.lwDevices.append(urwid.Text(('', self.up_Clients())))
        self.body.set_focus(len(self.lwDevices) - 1, 'above')

    def rm_ClientsTable(self, data):
        ''' remove client from table '''
        if self.table_clients  != []:
            for (host, ip, mac, vendor) in self.table_clients:
                if (mac == data):
                    self.table_clients.remove([host, ip, mac, vendor])
                    break
        self.lwDevices.clear()
        self.lwDevices.append(urwid.Text(('', self.up_Clients())))

    def up_Clients(self):
        if len(self.table_clients) > 0:
            return tabulate(self.table_clients,('Hostname','IpAddr','MacAddr','Vendor'))
        return ''

    def handleWindow(self, key):
        if key == 'R' or key == 'r':
            self.main_loop.draw_screen()
            self.lwDevices.clear()
            self.lwDevices.append(urwid.Text(('', self.up_Clients())))
        elif key == 'Q' or key == 'q' or key  == 'esc':
            raise urwid.ExitMainLoop()
