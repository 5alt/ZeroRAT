#!/usr/bin/python
# coding: UTF-8

import config
import sqlite3 as db

'''
TABLE client
    alive_time 为上次心跳包的时间

TABLE action
    status 0普通任务 1普通任务完成 2全局任务 3全局任务完成 4初始任务 5初始任务完成

'''

sql = ['''CREATE TABLE client(
    'signature' VARCHAR(32) PRIMARY KEY,
    'ip' VARCHAR(16) NOT NULL,
    'alive_time' INTEGER,
    'name' TEXT,
    'group' TEXT,
    'comment' TEXT
);''',
'''CREATE TABLE action(
    'id' INTEGER PRIMARY KEY,
    'pid' VARCHAR(32) NOT NULL,
    'signature' VARCHAR(32) NOT NULL,
    'action' TEXT NOT NULL,
    'payload' TEXT NOT NULL,
    'feedback' TEXT,
    'time' INTEGER,
    'status' INTEGER
);''',
'''CREATE TABLE uploadfiles(
    'id' INTEGER PRIMARY KEY,
    'signature' VARCHAR(32) NOT NULL,
    'pid' VARCHAR(32) NOT NULL,
    'originalname' VARCHAR(256) NOT NULL,
    'filename' VARCHAR(256) NOT NULL,
    'comment' TEXT
);''',
'''CREATE TABLE downloadfiles(
    'id' INTEGER PRIMARY KEY,
    'originalname' VARCHAR(256) NOT NULL,
    'filename' VARCHAR(256) NOT NULL,
    'comment' TEXT
);''']

conn = db.connect(config.DB_STRING)
cursor = conn.cursor()
for s in sql:
	cursor.execute(s)
conn.commit()