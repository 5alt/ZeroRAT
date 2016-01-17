#!/usr/bin/python
# coding: UTF-8
import sqlite

class download():
	def __init__(self):
		self.db = sqlite.sqlite()
	def add(self, originalname, filename):
		old = self.get(filename)
		if old:
			return self.db.update('downloadfiles', {'originalname':originalname}, {'filename': filename})
		else:
			data = {'originalname':originalname, 'filename':filename, 'comment': ''}
			return self.db.insert('downloadfiles', data)
	def delete(self, filename):
		return self.db.delete('downloadfiles', {'filename': filename})
	def setcomment(self, filename, comment):
		return self.db.update('downloadfiles', {'comment':comment}, {'filename': filename})
	def get(self, filename):
		sql = 'SELECT * FROM `downloadfiles` where filename=?'
		return self.db.fetchOne(sql, [filename])
	def getlist(self, limit=100, offset=0):
		sql = 'SELECT * FROM `downloadfiles` limit %d offset %d'%(limit, offset)
		return self.db.fetchAll(sql)
	def getbyname(self, filename):
		sql = 'SELECT * FROM `downloadfiles` where originalname=?'
		return self.db.fetchOne(sql, [filename])

if __name__ == '__main__':
	u = downlaod()
	filename = '6666'
	u.add('orig', filename)
	print u.get(filename)
	u.setcomment(filename, 'comment')
	print u.get(filename)
	u.delete(filename)
	print u.getlist()
