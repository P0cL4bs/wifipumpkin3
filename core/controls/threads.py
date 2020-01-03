import logging
import socket
from os import kill
import signal
from multiprocessing import Process, Queue
from subprocess import (Popen, STDOUT, PIPE)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QProcess, QObject
from core.packets.dhcpserver import DHCPProtocol
# from core.servers.proxy.http.controller.handler import MasterHandler
from core.utility.printer import display_messages,colors


class DHCPServerProcess(QThread):
    _ProcssOutput = pyqtSignal(object)
    def __init__(self,cmd ,directory_exec=None):
        QThread.__init__(self)
        self.directory_exec = directory_exec
        self.cmd = cmd

    def standardProcOutput(self,q):
        with Popen(self.cmd, bufsize=1, stdout=PIPE,stderr=STDOUT, universal_newlines=True) as p:
            for line in p.stdout:
                q.put(line)

    def run(self):
        self.queue = Queue()
        self.started = True
        self.procDHCP = Process(target=self.standardProcOutput, args=(self.queue,))
        self.procDHCP.start()
        print('[New Thread {} ({})]'.format(self.procDHCP.pid, self.objectName()))
        while self.started:
            self._ProcssOutput.emit(self.queue.get())

    def stop(self):
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
        self.procDHCP.terminate()
        self.started = False
        self.queue.close()



class ProcessThread(QThread):
    _ProcssOutput = pyqtSignal(object)
    def __init__(self,cmd ,directory_exec=None):
        QThread.__init__(self)
        self.directory_exec = directory_exec
        self.cmd = cmd


    @pyqtSlot()
    def getNameThread(self):
        return '[New Thread {} ({})]'.format(self.procThread.pid(),self.objectName())

    def readProcessOutput(self):
        self.data = str(self.procThread.readAllStandardOutput(),encoding='ascii')
        self._ProcssOutput.emit(self.data)

    def start(self):
        self.procThread = QProcess(self)
        self.procThread.setProcessChannelMode(QProcess.MergedChannels)
        if self.directory_exec:
            self.procThread.setWorkingDirectory(self.directory_exec)
        self.procThread.start(list(self.cmd.keys())[0],self.cmd[list(self.cmd.keys())[0]])
        self.procThread.readyReadStandardOutput.connect(self.readProcessOutput)
        print('[New Thread {} ({})]'.format(self.procThread.pid(),self.objectName()))

    def stop(self):
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
        if hasattr(self,'procThread'):
            self.procThread.terminate()
            self.procThread.waitForFinished()
            self.procThread.kill()



class DHCPServerProcess(QThread):
    _ProcssOutput = pyqtSignal(object)
    def __init__(self,cmd ,directory_exec=None):
        QThread.__init__(self)
        self.directory_exec = directory_exec
        self.cmd = cmd

    def standardProcOutput(self,q):
        with Popen(self.cmd, bufsize=1, stdout=PIPE,stderr=STDOUT, universal_newlines=True) as p:
            for line in p.stdout:
                q.put(line)

    def run(self):
        self.queue = Queue()
        self.started = True
        self.procDHCP = Process(target=self.standardProcOutput, args=(self.queue,))
        self.procDHCP.start()
        print('[New Thread {} ({})]'.format(self.procDHCP.pid, self.objectName()))
        while self.started:
            self._ProcssOutput.emit(self.queue.get())

    def stop(self):
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
        self.procDHCP.terminate()
        self.started = False
        self.queue.close()


class ProcessHostapd(QObject):
    statusAP_connected = pyqtSignal(object)
    statusAPError = pyqtSignal(object)
    def __init__(self,cmd,session):
        QObject.__init__(self)
        self.cmd         = cmd
        self.session     = session
        self.errorAPDriver = ('AP-DISABLED',
        'Failed to initialize interface',
        'nl80211 driver initialization failed.',
        'errors found in configuration file')
        self.msg_inactivity = []
        self.queue = Queue()
        self.started = False

    def read_OutputCommand(self):
        # for line in proc.stdout:
        #     if 'AP-STA-DISCONNECTED' in line.rstrip() or 'inactivity (timer DEAUTH/REMOVE)' in line.rstrip():
        #         q.put(line.split()[2])
        self.data = str(self.procHostapd.readAllStandardOutput(),encoding='ascii')
        if 'AP-STA-DISCONNECTED' in self.data.rstrip() or 'inactivity (timer DEAUTH/REMOVE)' in self.data.rstrip():
            self.statusAP_connected.emit(self.data.split()[2])
            #self.queue.put(self.data.split()[2])
        # #self.log_hostapd.info(self.data)
        # for error in self.errorAPDriver:
        #     if self.data.find(error) != -1:
        #         return self.statusAPError.emit(str(self.data))

    def getHostapdResponse(self):
        while self.started:
            self.msg_inactivity.append(self.queue.get())

    def start(self):
        self.makeLogger()
        self.procHostapd = QProcess(self)
        self.procHostapd.setProcessChannelMode(QProcess.MergedChannels)
        self.procHostapd.start(list(self.cmd.keys())[0],self.cmd[list(self.cmd.keys())[0]])
        self.procHostapd.readyReadStandardOutput.connect(self.read_OutputCommand)
        print('[New Thread {} ({})]'.format(self.procHostapd.pid(),self.objectName()))
        self.started = True
        # self.proc = Popen(self.cmd, bufsize=1, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        # self.procHostapd = Process(target=self.read_OutputCommand, args=(self.queue,self.proc))
        # self.procHostapd.start()
        print(display_messages('starting hostpad pid: [{}]'.format(self.procHostapd.pid),sucess=True))

    def makeLogger(self):
        #setup_logger('hostapd', C.LOG_HOSTAPD, self.session)
        #self.log_hostapd = logging.getLogger('hostapd')
        pass

    def stop(self):
        print('Thread::[{}] successfully stopped.'.format(self.objectName()))
        if hasattr(self,'procHostapd'):
            self.started = False
            #self.proc.kill()
            #self.proc.terminate()
            self.procHostapd.terminate()