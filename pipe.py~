#!/usr/bin/python
from scapy.all import *
from scapy.layers import http

stars = lambda n: "*" * n

q = list()
hostdict = {}
last_referer = "empty string that is not none"

def packethandler(pkt):
    global hostdict
    global last_referer
    host,referer = None,None
    for header in str(pkt).splitlines():
	if "Host" in header:
	    host = header[6:]
 	    #print "Host: " + host
	if "Referer"  in header:
	    parts = header[9:].split('//', 1)
	    referer = parts[0]+'//'+parts[1].split('/', 1)[0]
	    #print "Referer: " + referer
    if referer and referer in last_referer:
	if host in hostdict:
	    hostdict[host] += 1
	else:
	    hostdict[host] = 1
    if referer and referer not in last_referer:
	q.append({"referer":last_referer,"hosts":hostdict})
	last_referer = referer
        
def main():
    print("sniffing...")
    sniff(
        iface='eth0',
        prn= packethandler,
        lfilter=lambda p: "GET" in str(p),
        filter="tcp port 80")


main()



