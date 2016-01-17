#!/usr/bin/python
# coding: UTF-8
import sqlite

class upload():
	def __init__(self):
		self.db = sqlite.sqlite()
	def add(self, signature, pid, originalname, filename):
		data = {'signature': signature,'pid': pid, 'originalname':originalname, 'filename':filename}
		return self.db.insert('uploadfiles', data)
	def delete(self, filename):
		return self.db.delete('uploadfiles', {'filename': filename})
	def setcomment(self, filename, comment):
		return self.db.update('uploadfiles', {'comment':comment}, {'filename': filename})
	def get(self, filename):
		sql = 'SELECT * FROM `uploadfiles` where filename=?'
		return self.db.fetchOne(sql, [filename])
	def getbyclient(self, signature):
		sql = 'SELECT * FROM `uploadfiles` where signature=?'
		return self.db.fetchAll(sql, [signature])
	def getbypid(self, pid):
		sql = 'SELECT * FROM `uploadfiles` where pid=?'
		return self.db.fetchOne(sql, [pid])
	def getlist(self, limit=10, offset=0):
		sql = 'SELECT * FROM `uploadfiles` limit %d offset %d'%(limit, offset)
		return self.db.fetchAll(sql)

if __name__ == '__main__':
	u = uplaod()
	signature = '233'
	filename = '6666'
	u.add(signature, 'orig', filename)
	print u.get(filename)
	u.setcomment(filename, 'comment')
	print u.getbyclient(signature)
	u.delete(filename)
	print u.getlist()
