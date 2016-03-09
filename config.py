#!/usr/bin/python
# coding: UTF-8
import socket

def GetHostIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("baidu.com", 80))
	ip = s.getsockname()[0]
	s.close()
	return ip

host = GetHostIP()
port = 8080
SECRET_KEY = 'md5_salt'

upload_dir = "./uploads/"
download_dir = "./downloads/"


DB_STRING = "./jsrat.db"
PASSWORD = 'salt'