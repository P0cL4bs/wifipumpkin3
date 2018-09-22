from core.common.accesspoint import AccessPoint
from core.common.sniffing import SniffingPackets
from core.common.terminal import ConsoleUI
from core.widgets.window import ui_TableMonitorClient,ui_MonitorSniffer


class FrameworkBash(ConsoleUI):
    """
    :parameters
        options : parse_args
    """
    def __init__(self,options):
        ConsoleUI.__init__(self)
        self.options    = options
        self.sniffs     = SniffingPackets(self)
        self.ac         = AccessPoint('wlxc83a35cef744')
        self.ac.sendStatusPoint.connect(self.getAccessPointStatus)
        self.ui_table   = ui_TableMonitorClient(self)
        self.ui_monitor = ui_MonitorSniffer(self)


    def getAccessPointStatus(self,status):
        self.ui_table.setupThreads()
        self.ui_monitor.setupThreads()
        print('getAccessPointStatus() -> True')
        

    def do_start(self,args):
        ''' start access point '''
        self.sniffs.start()
        self.ac.start()

    def do_clients(self, args):
        ''' show all clients connected on AP '''
        self.ui_table.start()

    def do_monitor(self, args):
        ''' monitor traffic capture realtime Sniffer'''
        self.ui_monitor.start()


    def do_stop(self,args):
        ''' stop access point '''
        self.ac.stop()
        self.ui_table.stop()
        self.sniffs.stop()
