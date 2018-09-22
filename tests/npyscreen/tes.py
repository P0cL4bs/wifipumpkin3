from mitmproxy import master, controller, options
from mitmproxy.proxy import ProxyServer, ProxyConfig
import time
import threading

def background(f):
    '''
    a threading decorator
    use @background above the function you want to run in the background
    '''
    def bg_f(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return bg_f

class MProxy(master.Master):

    @background
    def run(self):
        try:
            master.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
            self.shutdown()

    @controller.handler
    def request(self, f):
        print("request", f)

    @controller.handler
    def response(self, f):
        print("response", f)

opts = options.Options(listen_port=8080,mode="transparent",cadir="~/.mitmproxy/")
config = ProxyConfig(opts)
server = ProxyServer(config)
m = MProxy(opts, server)
m.run()

time.sleep(60) # there is should be another code
m.shutdown()
