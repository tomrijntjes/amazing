#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Stichting z25.org
#
# AUTHOR:
# Arnaud Loonstra <arnaud@z25.org>

import os
#import pysvn # apt-get install python-svn / pip3 install pysvn
import sys
# boolean telling us if we are python3 or not
PY3 = sys.version_info[0] > 2

from json import dumps, dump
from json import loads, load
from webob import Response, Request, exc, dec
if PY3:
    import urllib.request, urllib.parse, urllib.error
else:
    import urllib

#import appie_utils
try:
    from webob import static
except ImportError:
    import _static as static


if not PY3:
    from io import open

class AppieRestObject(object):
    """
    template class for a simple REST object for Appie

    Inherit this class and override the methods you need
    """
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, environ, start_response):
        req = Request(environ)
        method = req.method
        try:
            handle_method = getattr(self, 'handle_'+method)
        except:
            raise exc.HTTPInternalServerError('No %s method on resource: %s' %(method,object))
        resp = handle_method(req)
        return resp(environ, start_response)

    def handle_GET(self, req, *args, **kwargs):
        return exc.HTTPMethodNotAllowed()

    def handle_POST(self, req, *args, **kwargs):
        return exc.HTTPMethodNotAllowed()

    def handle_PUT(self, req, *args, **kwargs):
        return exc.HTTPMethodNotAllowed()

    def handle_DELETE(self, req, *args, **kwargs):
        return exc.HTTPMethodNotAllowed()


class AppieJsonRestObject(AppieRestObject):
    """
    Example class handling json objects
    Still needs enhancing
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_json_GET(self, req, *args, **kwargs):
        ret = self.handle_GET(req, *args, **kwargs)
        retJSON = dumps(resp)
        return Response(retJSON, content_type="application/json")

    def handle_GET(self, req, *args, **kwargs):
        if req.content_type == "application/json":
            return self.handle_json_GET(req, *args, **kwargs)
        return exc.HTTPNotAcceptable("Only json mimetypes allowed")


class AppieSimpleFileServer(AppieRestObject):

    def __init__(self, root_dir="./", enable_del=False, *args, **kwargs):
        self.root_dir = root_dir
        super(AppieRestObject, self).__init__(*args, **kwargs)

    def handle_GET(self, req, *args, **kwargs):
        return static.DirectoryApp(self.root_dir)

    def handle_POST(self, req, *args, **kwargs):
        # uploading new files
        filename = req.path_info_pop()
        filepath = os.path.join(os.path.join(self._root_dir, filename))
        # if the file exists we raise an exception
        if filename == "":
            filename = req.params['file']
        if os.path.exists(filepath):
            return exc.HTTPForbidden("%s already exists" %filename)
        with open(os.path.join(self._root_dir, filename), 'wb') as saveFile:
            saveFile.write(self.req.body_file.read())
        saveFile.close()
        return exc.HTTPMethodAccepted("File uploaded")

    def handle_PUT(self, *args, **kwargs):
        if not enable_del:
            return exc.HTTPForbidden("%s permission denied" %filename)
        # This will overwrite files
        # uploading files to update
        filename = self.req.path_info_pop()
        filepath = os.path.join(os.path.join(self._root_dir, filename))
        # if the file doesn't exist we raise an exception
        if not os.path.exists(filepath):
            raise exc.HTTPNotFound("%s file not found" %filename)
        if filename == "":
            filename = req.params['file']
        with open(os.path.join(self._httpdRoot, filename), 'wb') as saveFile:
            saveFile.write(req.body_file.read())
        saveFile.close()
        return exc.HTTPMethodAccepted("File updated")

    def handle_DELETE(self, *args, **kwargs):
        if not enable_del:
            return exc.HTTPForbidden("%s permission denied" %filename)
        # This will overwrite files
        # uploading files to update
        filename = self.req.path_info_pop()
        filepath = os.path.join(os.path.join(self._root_dir, filename))
        # if the file doesn't exist we raise an exception
        if not os.path.exists(filepath):
            raise exc.HTTPNotFound("%s file not found" %filename)
        if filename == "":
            filename = req.params['file']
        with open(os.path.join(self._httpdRoot, filename), 'wb') as saveFile:
            saveFile.write(req.body_file.read())
        saveFile.close()
        return exc.HTTPMethodAccepted("File updated")


class Appie(object):
    """
    Basic class for providing a RESTful interface to resources.

    Simply register an AppieRestObject inherited class object

    GET = Retrieve
    PUT = Replace
    POST = New/Create
    DELETE = d'uh
    """
    def __init__(self, *args, **kwargs):
        # empty dict of restObjects
        self._restObjects = {}
        self._default = kwargs.pop('default', exc.HTTPNotFound('No such resource'))
        self._inject_headers = None
        for name in kwargs:
            self.register_rest_object(name, kwargs[name])

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self._process(req)
        except ValueError as e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException as e:
            resp = e
        return resp(environ, start_response)

    def register_rest_object(self, name, obj):
        print('Appie: registering url: /%s' %name)
        self._restObjects.update({name : obj})

    def unregister_rest_object(self, name):
        print('Appie: unregistering url: /%s' %name)
        try:
            del self._restObjects[name]
        except KeyError as ke:
            print("No such object: %s" %ke)

    def inject_headers(self, headers):
        self._inject_headers = headers

    def _process(self, req):
        """
        a request URL is parsed as follow
        /object/resource?args
        object is the main python object
        GET /object is mapped to handle_get function(**kwargs)
        GET /object/resource is mapped to handle_get([resource,], **kwargs)
        GET /object/resource/resource2 is mapped to handle_get([resource,resource2], **kwargs)
        args are always passed on through **kwargs
        """
        # GET, POST, PUT or DELETE
        method = req.method
        object = req.path_info_peek()

        if object in self._restObjects.keys():
            #remove the object from the request path
            req.path_info_pop()
            try:
                resp = req.get_response(self._restObjects[object], req)
            except Exception as e:
                #print(e)
                return exc.HTTPNotFound('No such resource: %s. err: %s' %(object, e))
        else:
            resp = req.get_response(self._default, req)
        # special for Roderick
        if (self._inject_headers):
            resp.headers.update(self._inject_headers)
        return resp


# Damned wsgi, we need to specify the path to the modules!
# import sys
# sys.path.append('/home/z25/www/webappie')

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    svn_root = "file:///home/projects/svn/"
    web_root = "../../../../../../z25-ict/web/www.z25.org/src/html/" # "/var/www/www2"
    static_root = "/tmp"
    projects_root = "../../../../../../z25-ict/web/appie/tst/"

    # get arguments from command line, skip DEF (DEF = DEFAULT)
    # first argument is the path to the projects dir (containing pub folders of each project)
    # second argument is the path to the static_root (static files will be copied here)
    # third argument is the path to the web_root (ex: /var/www/www2)
    # fourth argument is path (or url) to svn repo (ex: svn+ssh://projects.z25.org/home/projects/svn/ OR file:///home/projects/svn/)
    args = sys.argv
    if len(sys.argv) >= 5:
        if sys.argv[4] != "DEF":
            svn_root = sys.argv[4]
    if len(sys.argv) >= 4:
        if sys.argv[3] != "DEF":
            web_root = sys.argv[3]
    if len(sys.argv) >= 3:
        if sys.argv[2] != "DEF":
            static_root = sys.argv[2]
    if len(sys.argv) >= 2:
        if sys.argv[1] != "DEF":
            projects_root = sys.argv[1]
        
    # outp
    print("Projects_root = "+ projects_root)
    print("Static_root   = "+ static_root)
    print("Web_root      = "+ web_root)
    print("Svn_root      = "+ svn_root)

    # generate a simple http server
    # extra headers we want to inject in our responses
    extra_headers = {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
                        'Access-Control-Max-Age': '86400',
                        'Access-Control-Allow-Headers': 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
                    }
    # this the default file serving object serving files from the webroot
    # AppieFS = AppieSimpleFileServer("../../../../../../z25-ict/web/www.z25.org/src/html/", enable_del=True)
    AppieFS = AppieSimpleFileServer(web_root, enable_del=True)
    # create the Appie instance and pass it the default file server
    appie_inst = Appie(default=AppieFS)
    # add the extra header info to Appie
    appie_inst.inject_headers(extra_headers)
    # register simple Rest object serving file from the "static" url base
    # this serves the files for the z25 website
    appie_inst.register_rest_object("static", static.DirectoryApp(static_root))
    # register the z25 collector
    projects = AppieZ25Projects(projects_root, static_root, svn_root)
    appie_inst.register_rest_object("json", projects)

    # start a webserver
    httpd = make_server('', 8000, appie_inst)
    print("Serving on port 8000...")
    # Serve until process is killed
    httpd.serve_forever()
