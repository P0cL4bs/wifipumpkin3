from PyQt4.QtCore import QThread,pyqtSignal
from time import sleep,asctime,strftime
from threading import Thread
import queue
from scapy.all import *
import logging
from plugins.analyzers import *
from core.utility.collection import SettingsINI
import core.utility.constants as C
from core.utility.printer import display_messages,colors

"""
Description:
    This program is a core for wifi-pumpkin.py. file which includes functionality
    for TCPProxy Core.

"""

class TH_SniffingPackets(QThread):
    output_plugins = pyqtSignal(object)
    def __init__(self,interface,session):
        QThread.__init__(self)
        self.interface  = interface
        self.session    = session
        self.stopped    = False
        self.config     = SettingsINI(C.CONFIG_TP_INI)
        self.msg_output = []
        self.queue_plugins = queue.Queue()

    def run(self):
        self.main()

    def sniffer(self,q):
        while not self.stopped:
            try:
                sniff(iface=self.interface,
                      filter="tcp and ( port 80 )",
                      prn =lambda x : q.put(x), store=0)
            except Exception:pass
            if self.stopped:
                break

    def disablePlugin(self,name, status):
        ''' disable plugin by name '''
        plugin_on = []
        if status:
            for plugin in self.plugins:
                plugin_on.append(self.plugins[plugin].Name)
            if name not in plugin_on:
                for p in self.plugin_classes:
                    pluginconf = p()
                    if  pluginconf.Name == name:
                        self.plugins[name] = pluginconf
                        self.plugins[name].getInstance()._activated = True
                        #print('TCPProxy::{0:17} status:On'.format(name))
        else:
            #print('TCPProxy::{0:17} status:Off'.format(name))
            self.plugins.pop(self.plugins[name].Name)


    def get_output_activated(self):
        while not self.stopped:
           self.msg_output.append(self.queue_plugins.get())

    def main(self):
        self.plugins = {}
        self.plugin_classes = default.PSniffer.__subclasses__()
        for p in self.plugin_classes:
            plugin_load = p()
            self.plugins[plugin_load.Name] = plugin_load
            self.plugins[plugin_load.Name].output = self.queue_plugins
            self.plugins[plugin_load.Name].session = self.session

        for name in self.plugins.keys():
            if self.config.get('plugins', name, format=bool):
                self.plugins[name].getInstance()._activated = True
                #print('TCPProxy::{0:17} status:On'.format(name))
        q = queue.Queue()
        sniff = Thread(target =self.sniffer, args = (q,))
        sniff.start()
        while (not self.stopped):
            try:
                pkt = q.get(timeout = 0)
                for Active in self.plugins.keys():
                    if self.plugins[Active].getInstance()._activated:
                        try:
                            self.plugins[Active].filterPackets(pkt)
                        except Exception: pass
            except queue.Empty:
              pass

    def stop(self):
        self.stopped = True
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
