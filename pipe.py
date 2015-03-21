#!/usr/bin/python
from scapy.all import *
from scapy.layers import http

from Queue import Queue
from threading import Thread

stars = lambda n: "*" * n
q = Queue()


def worker():
    while True:
        pkt = q.get()
        #do something
        q.task_done()

        
def main():
    t = Thread(target=worker)
    t.daemon = True
    t.start()
    print("sniffing...")
    sniff(
        iface='eth0',
        prn=q.put(packet),
        lfilter=lambda p: "GET" in str(p),
        filter="tcp port 80")
    q.join()


main()


