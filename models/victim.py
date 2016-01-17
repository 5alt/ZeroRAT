#!/usr/bin/python
# coding: UTF-8
import time
import sqlite

class victim():
	def __init__(self):
		self.db = sqlite.sqlite()
	def add(self, signature, ip):
		data = {'signature': signature, 'ip':ip, 'alive_time':0, 'group':'default'}
		return self.db.insert('client', data)
	def delete(self, signature):
		return self.db.delete('client', {'signature': signature})
	def setcomment(self, signature, comment):
		return self.db.update('client', {'comment':comment}, {'signature': signature})
	def heartbeat(self, signature):
		return self.db.update('client', {'alive_time': int(time.time())}, {'signature': signature})
	def setname(self, signature, name):
		return self.db.update('client', {'name':name}, {'signature': signature})
	def setgroup(self, signature, group):
		return self.db.update('client', {'`group`':group}, {'signature': signature})
	def alives(self):
		sql = 'SELECT * FROM `client` where alive_time>%d'%(int(time.time())-60*5)
		return self.db.fetchAll(sql)
	def get(self, signature):
		sql = 'SELECT * FROM `client` where signature=?'
		return self.db.fetchOne(sql, [signature])
	def all(self, limit=10, offset=0):
		sql = 'SELECT * FROM `client` limit %d offset %d'%(limit, offset)
		return self.db.fetchAll(sql)
	def checkalive(self, signature):
		t = self.get(signature)['alive_time']
		if time.time()-t < 60:
			return True
		else:
			return False

if __name__ == '__main__':
	c = victim()
	signature = '2333223'
	print c.add(signature, '127.0.0.1')
	print c.get(signature)
	print c.alives()
	print c.all()
	print c.setcomment(signature, 'comment')
	print c.get(signature)
	print c.setgroup(signature, 'group')
	print c.get(signature)
	print c.setname(signature, 'name')
	print c.get(signature)
	print c.heartbeat(signature)
	print c.get(signature)
	print c.delete(signature)
	print c.get(signature)