#!/usr/bin/python
from scapy.all import *
from Queue import Queue
from threading import Thread

stars = lambda n: "*" * n
q = Queue()

def GET_print(packet):
    pkt =  "\n".join((
        stars(40) + "GET PACKET" + stars(40),
        "\n".join(packet.sprintf("{Raw:%Raw.load%}").split(r"\r\n")),
        stars(90)))
    q.put(pkt)

print("sniffing...")

def worker():
    while True:
        pkt = q.get()
        print("success")
        q.task_done()
        
def main():
    t = Thread(target=worker)
    t.daemon = True
    t.start()
    sniff(
        iface='eth0',
        prn=GET_print,
        lfilter=lambda p: "GET" in str(p),
        filter="tcp port 80")
    q.join()


main()



