from PyQt5 import QtCore, Qt
from functools import  partial

class DockableWidget(Qt.QObject):
    title = 'Default'
    id = 'default'
    addDock = QtCore.pyqtSignal(object)

    def __init__(self,parent=0,t='Default',info={}):
        super(DockableWidget,self).__init__()
        self.parent = parent
        self.title = t
        self.logger = info
        self.startThread = False
        self.processThread = None

    def runThread(self):
        self.startThread=True

    def controlui_toggled(self):
        if self.controlui.isChecked():
            self.addDock.emit(True)
        else:
            self.addDock.emit(False)

    def writeModeData(self,data):
        print(data)

    def clear(self):
        pass

    def stopProcess(self):
        if self.processThread != None:
            self.processThread.stop()
