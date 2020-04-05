#!/usr/bin/env python3

"""
Copyright (C) 2016  hjltu@ya.ru

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

create(tb_name) - create new table
    options: tb_name - table name
    return: 0 or 1
drop(tb_name) - drop table
    options: tb_name - table name
    return: 0 or 1
insert(tb_name, stat) - insert new row
    option: tb_name - table name, stat - new status
    return: 0 or 1
select(tb_name) - query last time and stat
    option: tb_name - table name
    return: {time: stat} or 1
select_between(tb_name, col, first, last) - query for all names and stat
    options: tb_name - table name
select_offset(tb_name, depth) - query for all names and stat
    options: tb_name - table name

"""

import sqlite3,time


DB_NAME = 'stat.db'


def create(tb_name='test'):
    tb_schema='id INTEGER PRIMARY KEY, stat INTEGER, time INTEGER, date TEXT'
    print('test',tb_name)
    query=('CREATE TABLE '+tb_name+'('+tb_schema+')')
    return my_cdi(query)


def drop(tb_name='test'):
    query=('DROP TABLE '+tb_name)
    return my_cdi(query)


def insert(tb_name='test',stat=0):
    query=('INSERT INTO '+tb_name+'(stat, time, date) VALUES(?,?,?)')
    return my_cdi(query, stat)


def select(tb_name='test'):
    query=('SELECT time,stat FROM '+tb_name+' WHERE id = (SELECT MAX(id)  FROM '+tb_name+')')
    return my_select(query)


def select_between(tb_name='test', col='id', first=0, last=0):
    query=('SELECT time,stat FROM '+tb_name+' WHERE '+col+' BETWEEN '+\
        str(first)+' AND '+str(last))
    return my_select(query)


def select_offset(tb_name='test', depth=1):
    query=('SELECT time,stat FROM '+tb_name+' LIMIT '+str(depth)+' OFFSET ' +
        '(SELECT COUNT (*) FROM '+tb_name+')-'+str(depth))
    return my_select(query)


def select_all(tb_name='test'):
    query=('SELECT time,stat FROM '+tb_name+'')
    return my_select(query)


def my_cdi(query, stat=None):
    db=sqlite3.connect(DB_NAME)
    cursor=db.cursor()
    try:
        if stat is None:
            cursor.execute(query)
        else:
            cursor.execute(query,(stat,time.time(), time.ctime()))
    except:
        db.rollback()
        return 1
    db.commit()
    db.close
    return 0


def my_select(query):
    db=sqlite3.connect(DB_NAME)
    cursor=db.cursor()
    try:
        cursor.execute(query)
    except:
        return 1
    rows=cursor.fetchall()
    if len(rows) == 0:
        db.close()
        return None
    else:
        db.close()
        return dict(rows)


import unittest

class TestStringMethods(unittest.TestCase):

    def test_mydb(self):
        # self.assertEqual(create(), 0)
        # self.assertEqual(insert(), 0)
        # self.assertNotEqual(select(), 1)
        # self.assertNotEqual(select(), 2)
        # self.assertNotEqual(selectall(), 1)
        # self.assertNotEqual(selectall(), 2)
        # self.assertEqual(update(), 0)
        # self.assertEqual(delete(), 0)
        # self.assertEqual(drop(), 0)
        print('all tests done')

if __name__=='__main__':
    unittest.main()
