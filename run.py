#!/usr/bin/python
# coding: UTF-8

'''
http://stackoverflow.com/questions/16945780/decoding-base64-in-batch  
Certutil has been around since at least Windows Server 2003. 

'''
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import os

from config import *
from controllers import client as client_controller
from controllers import server as admin_controller


from flask import Flask, request, make_response, render_template_string
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_module(admin_controller.server, url_prefix='/server')
app.register_module(client_controller.client)


if not os.path.exists(upload_dir):
    os.mkdir(upload_dir, 0700)

if not os.path.exists(download_dir):
    os.mkdir(download_dir, 0700)


if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()
    #app.run(host="0.0.0.0", port=port, debug=True)

