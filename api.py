#!/usr/bin/python
import sys
sys.path.append('py')
import appie
import webob
import json
import threading
from Queue import Queue

from scapy.all import *

class SniffThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
        self.hostdict = {}
        self.last_referer = ""
        self.setDaemon(True)

    def packethandler(self, pkt):
        host,referer = None,None
        for header in str(pkt).splitlines():
            if "Host" in header:
                host = header[6:]
                #print "Host: " + host
            if "Referer"  in header:
                parts = header[9:].split('//', 1)
                referer = parts[0]+'//'+parts[1].split('/', 1)[0]
            if host and referer:
                self.q.put(host,referer)
       
    def run(self):
        try:
            sniff(
                iface='eth0',
                prn= self.packethandler,
                lfilter=lambda p: "GET" in str(p),
                filter="tcp port 80")
        except:
            return


class AmazingApi(appie.AppieRestObject):
    
    def __init__(self, q, *args, **kwargs):
        super(AmazingApi, self).__init__(args, kwargs)
        self.q = q
        self.count = 0;

    def handle_GET(self, req, *args, **kwargs):
        self.count += 1
        d = dict()
        while not q.empty():
            host,referer  = q.get()
            if referer in d:
                if host in d[referer]:
                     d[referer][host] +=1
                else:
                     d[referer][host] = 1
            else:
                d[referer][host] = 1
        q.task_done()
        return webob.Response(json.dumps(d), content_type="application/json")


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    AppieFS = appie.AppieSimpleFileServer("html", enable_del=True)
    q = Queue()
    amaze = AmazingApi(q)
    appie_inst = appie.Appie(default=AppieFS)
    appie_inst.register_rest_object("api", amaze)

    # sniffer thread    
    t = SniffThread(q)
    t.start()

    # start a webserver
    httpd = make_server('', 8000, appie_inst)
    print("Serving on port 8000...")
    # Serve until process is killed
    httpd.serve_forever()
    print("exit")
    
