from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
import weakref
from loguru import logger
import sys
import json

def make_filter(name):
    def filter(record):
        return record["extra"].get("name") == name
    return filter


class StandardLog:
    _typelog  = None
    _serialized = False
    _colorized  = True
    _ignore  = False
    _config    = None
    _file_name = 'file.log'
    _bgcolor = str()
    _color = str()
    _extra = {}

    def __init__(self, typelog, colorize = False , serialize = False , **kwargs):
        self.typelog = typelog
        self.colorized = colorize
        self.serialized = serialize
        self.color = kwargs['config'].get('color')
        self.bgcolor = kwargs['config'].get('bg_color')
        self.extra = kwargs['config'].get('extra')
        self.logger = logger.bind(name=self.typelog, specific=True)

    def configure(self):
        logger.configure(**self.config)

    def redirect_stdout(self):
        if (self.ignore):
            return os.devnull
        return sys.stdout

    @property
    def config(self):
        self._config = {
        "handlers": [
            {
                "sink": self.redirect_stdout(),"colorize": self.colorized,
                "filter" : make_filter(self.typelog),
                "format": " [<bg %s> <%s> {extra[name]} </%s> </bg %s>] {time:HH:mm:ss}  - {message} "%(self.bgcolor,self.color,self.color, self.bgcolor)
             },

            {   "sink": self.filename,
                "serialize": self.serialized,
                "format": "{time:YYYY-MM-DD at HH:mm:ss} {level} - {message}",
                "filter" : make_filter(self.typelog)
            },
         ],
        "extra": self.extra
        }
        return self._config

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, data):
        self._extra = data

    @property
    def typelog(self):
        return self._typelog

    @typelog.setter
    def typelog(self, name):
        self._typelog = name
    
    @property
    def filename(self):
        return self._file_name

    @filename.setter
    def filename(self, path):
        self._file_name = path
        self.configure()

    @property
    def serialized(self):
        return self._serialized

    @serialized.setter
    def serialized(self, status):
        self._serialized = status

    @property
    def colorized(self):
        return self._colorized

    @colorized.setter
    def colorized(self, status):
        self._colorized = status

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
    
    @property
    def bgcolor(self):
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self , value):
        self._bgcolor = value

    @property
    def ignore(self):
        return self._ignore

    @ignore.setter
    def ignore(self , value):
        self._ignore = value

    def setIgnore(self, value):
        self.ignore = value
        self.configure()

    def info(self, message):
        self.configure()
        self.logger.info(message)

    def debug(self, message):
        self.configure()
        self.logger.debug(message)


class LoggerManager(CoreSettings):
    Name = "Logger Manager"
    ID = "Logger"
    Category = "Logger"
    instances = []
    _loggers = {}

    @classmethod
    def getInstance(cls):
        return cls.instances[0]

    def __init__(self, parent):
        super(LoggerManager, self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))
        self.conf = SuperSettings.getInstance()

        self.title = self.__class__.__name__

    def add(self, ID ,logger=StandardLog):
        self._loggers[ID] = logger

    def get(self, ID):
        return self._loggers.get(ID)
    
    def all(self):
        return self._loggers.keys()

    def getExtraConfig(self, name):
        color = self.conf.get('colors_log', name,format=list)
        config_extra = { "color" : color[0] , 
            "extra" : {'dns': 0x90}, "bg_color" : color[1] }
        return config_extra