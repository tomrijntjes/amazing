import bge
import mathutils
import random
import json
import time

class z25MsgController(object):
    def __init__(self):
        self.log("Init")
        self._curScene = bge.logic.getCurrentScene()
        self._objects = objects = self._curScene.objects
        self._cont = bge.logic.getCurrentController()
        self._own = self._cont.owner
        c = self._cont.sensors.get("z25MsgController")
        self._msgSensor = c
    
    def parseMessage(self):
        """
        Parse subjects to match to a function or execute default.
        supply body as a argument to function
        """
        if bge.logic.getCurrentController().sensors["z25MsgController"].positive:
            if not self._msgSensor:
                self._msgSensor = bge.logic.getCurrentController().sensors.get("z25MsgController")
            for i in range(len(self._msgSensor.subjects)):
                subject = self._msgSensor.subjects[i]
                body = self._msgSensor.bodies[i]
                self.log(subject)
                try:
                    func = getattr(self, subject)
                except Exception as err:
                    print("couldn't link message", subject, "to function executing default with arg:", body, "ERROR:", str(err))
                    self._default(subject)
                else:
                    func(body)

    def _default(self, *arg):
        self.log("No function: ",arg," here Pal, Sorry !")

    def log(self, *arg):
        print("z25MsgController:", *arg)

class amazeObject(object):
    
    objs = []
    MAXLIFE = 45
    
    def __init__(self, gobj, host, danger, score):
        self.gobj = gobj
        self.host = host
        self.danger = danger
        self.score = score
        self.spawnts = time.time()
        self.xforce = random.random() * 2 -1.0
        self.to_delete = False
        amazeObject.objs.append(self)

    def update(self):
        #print(self.gobj.worldPosition.z)
        if self.gobj.worldPosition.z > 10 or self.spawnts + 10 < time.time():
            self.gobj.endObject()
            self.to_delete = True

        if self.danger > 0.4:
            self.gobj.applyForce([self.xforce*12,0, 11+12*self.danger])


class amazeController(z25MsgController):
    
    def __init__(self):
        print("hmm")
        z25MsgController.__init__(self)
        self._cube = self._curScene.objectsInactive['LogoPlane']
        self._root = self._curScene.objects['ScriptHolder']
        
    def addObject(self, obj):
        newObj = self._curScene.addObject(obj, self._root)
        #newObj.setParent(self._root)
        return newObj
    
    def addHost(self, *args):
        data = json.loads(args[0])
        new_obj_ref = self._curScene.objectsInactive.get(data['host'], self._cube)
        obj = self.addObject(new_obj_ref)
        #print(data['host'])
        danger = 1.0-data.get('danger')
        print("DANGER:", danger)
        if danger < 0.3: danger = 0
        amazeObject(obj, data.get('host'), 1.0-data.get('danger'), data.get('score'))
    
    def update(self):
        d = []
        for o in amazeObject.objs:
            if o.to_delete:
                d.append(o)
            else:
                o.update()
        for o in d:
            amazeObject.objs.remove(o)
        
        #print("update")
        
    def q(self, *args):
        print("adding")
        obj = self.addObject(self._cube)
        amazeObject(obj, 1.0)

    def w(self, *args):
        print("adding")
        obj = self.addObject(self._cube)
        amazeObject(obj, -1.0)


# Make functions accesible for the sensors..
def parseMessage():
    ctrl.parseMessage()

def update():
    if not ctrl:
        print('bah')
    else:
        ctrl.update()

ctrl = amazeController()
