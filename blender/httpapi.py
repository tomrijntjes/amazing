import bge
import mathutils
import random
import urllib.request
import json
from tldextract import tldextract

test = {'http://www.telegraaf.nl': {'www.google-analytics.com': {'count': 8, 'danger_index': 0.13374060253034678}}, 'http://www.marktplaats.nl': {'pagead2.googlesyndication.com': {'count': 12, 'danger_index': 0.9}}, 'http://rs.gwallet.com': {'b.scorecardresearch.com': {'count': 12, 'danger_index': 0.014822218604072823}}, 'http://tmgonlinemedia.nl': {'www.telegraaf.nl': {'count': 4, 'danger_index': 0.1703561984676167}}, 'http://csmcampagne.consumind.nl': {'csmcampagne.consumind.nl': {'count': 4, 'danger_index': 0.7095237636199369}}, 'http://community-cdn.telegraaf.nl': {'www.telegraaf.nl': {'count': 5, 'danger_index': 0.37300164208073483}}, 'http://fonts.googleapis.com': {'fonts.gstatic.com': {'count': 4, 'danger_index': 0.643813754740509}}, 'http://telegraaf.tcdn.nl': {'telegraaf.tcdn.nl': {'count': 4, 'danger_index': 0.09192799478017158}}, 'http://optimized-by.rubiconproject.com': {'dsp.adledge.com': {'count': 4, 'danger_index': 0.05214278473647753}}, 'http://cdn.turn.com': {'pixel.rubiconproject.com': {'count': 8, 'danger_index': 0.7652698288701214}}, 'http://i.r1-cdn.net': {'i.r1-cdn.net': {'count': 12, 'danger_index': 0.7071093599743596}}}

class SniffData(object):

    def __init__(self):
        print("Http Init")
        self._curScene = bge.logic.getCurrentScene()
        self._objects = objects = self._curScene.objects
        self._cont = bge.logic.getCurrentController()
        self._own = self._cont.owner
        self.hosts = {}
        self.url = "http://localhost:8000/api"
        #self.parse_data(test)
        
    def parse_data(self, data):
        for host, referers in data.items():
            #print("object: ", host, tldextract.extract(host))
            tld = tldextract.extract(host)
            self.send_msg(tld.domain)
            for referer, score in referers.items():
                tld = tldextract.extract(referer)
                print("refobject", tld.domain, "score:", score.get('count'), score.get('danger_index'))
                self.send_msg(tld.domain, score.get('count'),  score.get('danger_index'))
                
    def send_msg(self, host, score=0, danger=0):
        bge.logic.sendMessage('addHost', json.dumps({'host': host, 'score': score, 'danger': danger}))

    def get_data(self):
        data = urllib.request.urlopen(self.url).read()
        self.parse_data(json.loads(data.decode('utf-8')))
    
# Make functions accesible for the sensors..
def getData():
    sniff.get_data()

def boe():
    print("bla")

sniff = SniffData()
