#!/usr/bin/python
import sys
sys.path.append('py')
import appie

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    AppieFS = appie.AppieSimpleFileServer(".", enable_del=True)
    appie_inst = appie.Appie(default=AppieFS)
    # start a webserver
    httpd = make_server('', 8000, appie_inst)
    print("Serving on port 8000...")
    # Serve until process is killed
    httpd.serve_forever()

