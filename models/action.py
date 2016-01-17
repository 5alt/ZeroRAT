#!/usr/bin/python
# coding: UTF-8
import time
import sqlite
import hashlib

class action():
	def __init__(self):
		self.db = sqlite.sqlite()
	def add(self, pid, signature, action, payload, status=0):
		data = {'pid':pid, 'signature': signature, 'action':action, 'payload':payload, 'time':0, 'status':status}
		return self.db.insert('action', data)
	def delete(self, pid):
		return self.db.delete('action', {'pid': pid})
	def get(self, pid):
		sql = 'SELECT * FROM `action` WHERE pid=? ORDER BY id DESC LIMIT 1'
		return self.db.fetchOne(sql, [pid])
	def gettask(self, signature):
		sql = 'SELECT * FROM `action` WHERE signature=? AND (status%2)=0 ORDER BY id DESC LIMIT 1'
		return self.db.fetchOne(sql, [signature])
	def setfeedback(self, pid, feedback):
		data = self.get(pid)
		if not data:
			return False
		if data['status']%2 == 0:
			return self.db.update('action', {'feedback':feedback, 'time':int(time.time()), 'status': data['status']+1}, {'pid': pid})
	def addglobaltask(self, signature, action, payload):
		'''
		不同的global task pid不同，但是同一个global task不同client pid相同
		'''
		pid = hashlib.md5(payload+signature).hexdigest()
		sql = 'SELECT * FROM `action` WHERE signature=? AND pid=? ORDER BY id DESC LIMIT 1'
		data = self.db.fetchOne(sql, [signature, pid])
		if not data:
			self.add(pid, signature, action, payload, 2)
			return True
		else:
			return False

if __name__ == '__main__':
	a = action()
	pid = '666666'
	signature = '2333223'
	print a.add(pid, signature, 'action', 'payload')
	print a.get(pid)
	print a.gettask(signature)
	print a.setfeedback(pid, 'feedback')
	print a.get(pid)
	print a.addglobaltask(signature, 'action', 'ppppppload')
	print a.get(pid)
	print a.delete(pid)
	print a.gettask(signature)