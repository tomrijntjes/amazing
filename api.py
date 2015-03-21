#!/usr/bin/python
import sys
sys.path.append('py')
import appie
import webob
import json

class AmazingApi(appie.AppieRestObject):
    
    def handle_GET(self, req, *args, **kwargs):
        return webob.Response(json.dumps({'test': "test"}), content_type="application/json")


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    AppieFS = appie.AppieSimpleFileServer("html", enable_del=True)
    amaze = AmazingApi()
    appie_inst = appie.Appie(default=AppieFS)
    appie_inst.register_rest_object("api", amaze)
    # start a webserver
    httpd = make_server('', 8000, appie_inst)
    print("Serving on port 8000...")
    # Serve until process is killed
    httpd.serve_forever()
