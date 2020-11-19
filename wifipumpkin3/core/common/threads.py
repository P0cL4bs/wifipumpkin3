from multiprocessing import Process, Queue
from subprocess import Popen, STDOUT, PIPE
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QProcess, QObject
from wifipumpkin3.core.utility.printer import display_messages
from wifipumpkin3.core.common.platforms import Linux as Refactor
import wifipumpkin3.core.utility.constants as C

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class DHCPServerProcess(QThread):
    _ProcssOutput = pyqtSignal(object)

    def __init__(self, cmd, directory_exec=None):
        QThread.__init__(self)
        self.directory_exec = directory_exec
        self.cmd = cmd

    def standardProcOutput(self, q):
        with Popen(
            self.cmd, bufsize=1, stdout=PIPE, stderr=STDOUT, universal_newlines=True
        ) as p:
            for line in p.stdout:
                q.put(line)

    def run(self):
        self.queue = Queue()
        self.started = True
        self.procDHCP = Process(target=self.standardProcOutput, args=(self.queue,))
        self.procDHCP.start()
        print("[New Thread {} ({})]".format(self.procDHCP.pid, self.objectName()))
        while self.started:
            self._ProcssOutput.emit(self.queue.get())

    def getpid(self):
        """ return the pid of current process in background"""
        return self.procDHCP.pid

    def getID(self):
        """ return the name of process in background"""
        return self.objectName()

    def stop(self):
        print("Thread::[{}] successfully stopped.".format(self.objectName()))
        self.procDHCP.terminate()
        self.started = False
        self.queue.close()


class ProcessThread(QThread):
    _ProcssOutput = pyqtSignal(object)

    def __init__(self, cmd, directory_exec=None):
        QThread.__init__(self)
        self.directory_exec = directory_exec
        self.cmd = cmd

    @pyqtSlot()
    def getNameThread(self):
        return "[New Thread {} ({})]".format(self.procThread.pid(), self.objectName())

    def readProcessOutput(self):
        try:
            self.data = str(self.procThread.readAllStandardOutput(), encoding="ascii")
            self._ProcssOutput.emit(self.data)
        except Exception:
            pass

    def getpid(self):
        """ return the pid of current process in background"""
        return self.procThread.pid()

    def getID(self):
        """ return the name of process in background"""
        return self.objectName()

    def start(self):
        self.procThread = QProcess(self)
        self.procThread.setProcessChannelMode(QProcess.MergedChannels)
        if self.directory_exec:
            self.procThread.setWorkingDirectory(self.directory_exec)
        self.procThread.start(
            list(self.cmd.keys())[0], self.cmd[list(self.cmd.keys())[0]]
        )
        self.procThread.readyReadStandardOutput.connect(self.readProcessOutput)
        print(
            display_messages(
                "starting {} pid: [{}]".format(
                    self.objectName(), self.procThread.pid()
                ),
                sucess=True,
            )
        )

    def stop(self):
        print(
            display_messages(
                "thread {} successfully stopped".format(self.objectName()), info=True
            )
        )
        if hasattr(self, "procThread"):
            self.procThread.terminate()
            self.procThread.waitForFinished()
            self.procThread.kill()


class DHCPServerProcess(QThread):
    _ProcssOutput = pyqtSignal(object)

    def __init__(self, cmd, directory_exec=None):
        QThread.__init__(self)
        self.directory_exec = directory_exec
        self.cmd = cmd

    def standardProcOutput(self, q):
        with Popen(
            self.cmd, bufsize=1, stdout=PIPE, stderr=STDOUT, universal_newlines=True
        ) as p:
            for line in p.stdout:
                q.put(line)

    def run(self):
        self.queue = Queue()
        self.started = True
        self.procDHCP = Process(target=self.standardProcOutput, args=(self.queue,))
        self.procDHCP.start()
        print("[New Thread {} ({})]".format(self.procDHCP.pid, self.objectName()))
        while self.started:
            self._ProcssOutput.emit(self.queue.get())

    def stop(self):
        print("Thread::[{}] successfully stopped.".format(self.objectName()))
        self.procDHCP.terminate()
        self.started = False
        self.queue.close()


class ProcessHostapd(QObject):
    statusAP_connected = pyqtSignal(object)
    statusAPError = pyqtSignal(object)
    signalApIsRuning = pyqtSignal(bool)

    def __init__(self, cmd, session):
        QObject.__init__(self)
        self.cmd = cmd
        self.session = session
        self.errorAPDriver = (
            "AP-DISABLED",
            "Failed to initialize interface",
            "nl80211 driver initialization failed.",
            "errors found in configuration file",
        )
        self.msg_inactivity = []
        self.queue = Queue()
        self.isRunning = False
        self.started = False

    def getpid(self):
        """ return the pid of current process in background"""
        return self.procHostapd.pid()

    def getID(self):
        """ return the name of process in background"""
        return self.objectName()

    def removeInactivityClient(self, client_mac):
        all_clients = Refactor.readFileDataToJson(C.CLIENTS_CONNECTED)
        if client_mac in all_clients.keys():
            del all_clients[client_mac]
        Refactor.writeFileDataToJson(C.CLIENTS_CONNECTED, all_clients)

    def read_OutputCommand(self):
        self.data = str(self.procHostapd.readAllStandardOutput(), encoding="ascii")
        if (
            "AP-STA-DISCONNECTED" in self.data.rstrip()
            or "inactivity (timer DEAUTH/REMOVE)" in self.data.rstrip()
        ):
            self.removeInactivityClient(self.data.split()[2])
            self.statusAP_connected.emit(self.data.split()[2])
        # check error hostapd log
        for error in self.errorAPDriver:
            if self.data.find(error) != -1:
                return self.statusAPError.emit(self.data)
        # process hostapd is running
        if self.started and not self.isRunning:
            self.signalApIsRuning.emit(True)
            self.isRunning = True

    def start(self):
        self.procHostapd = QProcess(self)
        self.procHostapd.setProcessChannelMode(QProcess.MergedChannels)
        self.procHostapd.start(
            list(self.cmd.keys())[0], self.cmd[list(self.cmd.keys())[0]]
        )
        self.procHostapd.readyReadStandardOutput.connect(self.read_OutputCommand)
        self.started = True
        print(
            display_messages(
                "starting hostpad pid: [{}]".format(self.procHostapd.pid()), sucess=True
            )
        )

    def stop(self):
        print(
            display_messages(
                "thread {} successfully stopped".format(self.objectName()), info=True
            )
        )
        if hasattr(self, "procHostapd"):
            self.started = False
            self.isRunning = False
            self.procHostapd.terminate()


class WorkerProcess(QThread):
    sendOutput = pyqtSignal(str)

    def __init__(self, command):
        super(WorkerProcess, self).__init__()
        self.process = QProcess(self)
        self.command = command

    def __del__(self):
        try:
            self.process.terminate()
            self.process.kill()
        except Exception:
            pass

    def start(self):
        self.setupProcess()

    def setupProcess(self):
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.start(
            list(self.command.keys())[0], self.command[list(self.command.keys())[0]]
        )
