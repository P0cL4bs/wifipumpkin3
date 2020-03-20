from struct import pack
from time import sleep,asctime
from random import randint
from base64 import b64encode
from os import popen,path,walk,stat,kill,remove
from subprocess import check_output,Popen,PIPE,STDOUT,CalledProcessError,call
from re import search,compile,VERBOSE,IGNORECASE
import netifaces
from scapy.all import *
from PyQt5 import QtCore
from PyQt5 import QtGui
import logging
import signal
import configparser
import wifipumpkin3.core.utility.constants as C
from shlex import split
from glob import glob
import warnings, json


loggers = {}
'''http://stackoverflow.com/questions/17035077/python-logging-to-multiple-log-files-from-different-classes'''
def setup_logger(logger_name, log_file,key=str(), level=logging.INFO):
    global loggers
    if loggers.get(logger_name):
        return loggers.get(logger_name)
    else:
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        formatter = logging.Formatter('SessionID[{}] %(asctime)s : %(message)s'.format(key))
        fileHandler = logging.FileHandler(log_file, mode='a')
        fileHandler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(fileHandler)
    return logger


class Linux(QtCore.QObject):

    @staticmethod
    def set_ip_forward(value):
        '''set forward to redirect packets '''
        with open(C.IPFORWARD, 'w') as file:
            file.write(str(value))
            file.close()
    '''
    http://stackoverflow.com/questions/159137/getting-mac-address
    '''
    @staticmethod
    def getHwAddr(ifname):
        ''' another functions for get mac adreess '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = ioctl(s.fileno(), 0x8927,  pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])

    @staticmethod
    def kill_procInterfaceBusy():
        ''' kill network processes are keeping the interface busy '''
        willkill = ('wpa_supplicant','dhclient') # for ethernet conntion
        pass

    @staticmethod
    def get_interfaces():
        ''' get interfaces and check status connection '''
        interfaces = {'activated':[None,None],'all':[],'gateway':None,'IPaddress': None}
        interfaces['all'] = netifaces.interfaces()
        try:
            interfaces['gateway'] = netifaces.gateways()['default'][netifaces.AF_INET][0]
            interfaces['activated'][0] = netifaces.gateways()['default'][netifaces.AF_INET][1]
            interfaces['IPaddress'] = netifaces.ifaddresses(interfaces['activated'][0])[netifaces.AF_INET][0]['addr']
            # check type interfaces connected with internet
            itype = None
            iface = interfaces['activated'][0]
            if iface[:-1] in ['ppp']:
                itype = 'ppp'
            elif iface[:2] in ['wl', 'wi', 'ra', 'at']:
                itype = 'wireless'
            elif iface[:2] in ['en','et']:
                itype = 'ethernet'
            interfaces['activated'][1] = itype
        except KeyError:
            pass
        return interfaces


    @staticmethod
    def get_Ipaddr(card):
        ''' get ipadress by interface name'''
        if card == None:
            return get_if_addr('{}'.format(Linux.get_interfaces()['activated'][0]))
        return get_if_addr('{}'.format(card))

    @staticmethod
    def get_mac(host):
        ''' return mac by ipadress local network '''
        fields = popen('grep "%s " /proc/net/arp' % host).read().split()
        if len(fields) == 6 and fields[3] != "00:00:00:00:00:00":
            return fields[3]
        else:
            return None

    @staticmethod
    def get_interface_mac(device):
        ''' get mac from interface local system '''
        result = check_output(["ifconfig", device], stderr=STDOUT, universal_newlines=True)
        m = search("(?<=HWaddr\\s)(.*)", result)
        n = search("(?<=ether\\s)(.*)", result)
        if hasattr(m, "group") : return m.group(0).strip()
        if hasattr(n, "group") : return n.group(0).split()[0]
        return None

    @staticmethod
    def randomMacAddress(prefix):
        '''generate random mac for prefix '''
        for ount in range(6-len(prefix)):
            prefix.append(randint(0x00, 0x7f))
        return ':'.join(map(lambda x: "%02x" % x, prefix))


    @staticmethod
    def check_is_mac(value):
        '''check if mac is mac type '''
        checked = compile(r"""(
         ^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$
        |^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$
        )""",VERBOSE|IGNORECASE)
        if checked.match(value) is None:return False
        else:
            return True

    @staticmethod
    def find(name, paths):
        ''' find all files in directory '''
        for root, dirs, files in walk(paths):
            if name in files:
                return path.join(root, name)
    @staticmethod
    def getSize(filename):
        ''' return files size by pathnme '''
        st = stat(filename)
        return st.st_size

    @staticmethod
    def writeFileDataToJson(filename, content, mode='w'):
        if (path.isfile(filename)):
            with open(filename, mode) as f:
                json.dump(content, f)

    @staticmethod
    def readFileDataToJson(filename, mode='r'):
        datastore = None
        if (path.isfile(filename)):
            with open(filename, mode) as f:
                datastore = json.load(f)
        return datastore


def is_hexadecimal(text):
    try:
        int(text, 16)
    except ValueError:
        return False
    else:
        return True

def is_ascii( text):
    try:
        text.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def exec_bash(command):
    ''' run command on background hide output'''
    popen(command+' > /dev/null')

def del_item_folder(directorys):
    ''' delete all items in folder '''
    for folder in directorys:
        files = glob(folder)
        for file in files:
            if path.isfile(file) and not '.py' in file:
                remove(file)



class decoded(object):
    """
    Deprecated: You can now directly use :py:attr:`content`.
    :py:attr:`raw_content` has the encoded content.
    """

    def __init__(self, message):  # pragma no cover
        warnings.warn("decoded() is deprecated, you can now directly use .content instead. "
                      ".raw_content has the encoded content.", DeprecationWarning)

    def __enter__(self):  # pragma no cover
        pass

    def __exit__(self, type, value, tb):  # pragma no cover
        pass




def hexdump( src, length=16, sep='.' ):
	'''
	https://gist.github.com/ImmortalPC/c340564823f283fe530b
	@brief Return {src} in hex dump.
	@param[in] length	{Int} Nb Bytes by row.
	@param[in] sep		{Char} For the text part, {sep} will be used for non ASCII char.
	@return {Str} The hexdump
	@note Full support for python2 and python3 !
	'''
	result = [];

	# Python3 support
	try:
		xrange(0,1);
	except NameError:
		xrange = range;

	for i in xrange(0, len(src), length):
		subSrc = src[i:i+length];
		hexa = '';
		isMiddle = False;
		for h in xrange(0,len(subSrc)):
			if h == length/2:
				hexa += ' ';
			h = subSrc[h];
			if not isinstance(h, int):
				h = ord(h);
			h = hex(h).replace('0x','');
			if len(h) == 1:
				h = '0'+h;
			hexa += h+' ';
		hexa = hexa.strip(' ');
		text = '';
		for c in subSrc:
			if not isinstance(c, int):
				c = ord(c);
			if 0x20 <= c < 0x7F:
				text += chr(c);
			else:
				text += sep;
		result.append(('%08X:  %-'+str(length*(2+1)+1)+'s  |%s|') % (i, hexa, text));

	return '\n'.join(result);