from random import randint
from scapy.all import *
from wifipumpkin3.plugins.analyzers.default import PSniffer
from os.path import splitext
from string import ascii_letters

class ImageCap(PSniffer):
    ''' capture image content http'''
    _activated     = False
    _instance      = None
    meta = {
        'Name'      : 'imageCap',
        'Version'   : '1.0',
        'Description' : 'capture image content http',
        'Author'    : 'Pumpkin-Dev',
    }
    def __init__(self):
        for key,value in self.meta.items():
            self.__dict__[key] = value

    @staticmethod
    def getInstance():
        if ImageCap._instance is None:
            ImageCap._instance = ImageCap()
        return ImageCap._instance

    def filterPackets(self,pkt):
        pass

    def random_char(self,y):
           return ''.join(random.choice(ascii_letters) for x in range(y))
