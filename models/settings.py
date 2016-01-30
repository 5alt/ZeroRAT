#!/usr/bin/python
# coding: UTF-8
import sqlite

class settings:
	def __init__(self):
		self.db = sqlite.sqlite()
	def set(self, key, value):
		try:
			data = {'key': key,'value': value}
			self.db.insert('settings', data)
		except:
			self.db.update('settings', {'value':value}, {'key': key})
	def delete(self, key):
		return self.db.delete('settings', {'key': key})
	def update(self, key, value):
		return self.db.update('settings', {'value':value}, {'key': key})
	def get(self, key):
		sql = 'SELECT * FROM `settings` where key=?'
		try:
			return self.db.fetchOne(sql, [key])['value']
		except:
			return ''

if __name__ == '__main__':
	s = settings()
	s.set('sss', 'ddd')
	print s.get('sss')
	s.set('sss', 'dddssss')
	print s.get('sss')
	s.delete('sss')
	print s.get('sss')