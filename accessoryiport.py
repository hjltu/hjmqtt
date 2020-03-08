#!/usr/bin/env python3

"""
accessoryiport.py

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
"""
""" iport tcp 192.168.0.20:10001
    topic:
        /iport/out
    push: {
        "deviceid":"SurfaceMount",
        "model":"iPortSM10B",
        "macaddr":"DC82F600100C",
        "version":"V6",
        "uptime":"1875573",
        "eventtime":"40565",
        "events":[{"label":"key 1","state":"1"}]}
    release: {
        "deviceid":"SurfaceMount",
        "model":"iPortSM10B",
        "macaddr":"DC82F600100C",
        "version":"V6",
        "uptime":"1875594",
        "eventtime":"40586",
        "events":[{"label":"key 1","state":"0"}]} """


import statdb
import time
import math
import datetime as dt


class Start(object):

    """ add homekit name in database if its not exist
    """
    def __init__(self, acc, prefix='/homekit/'):
        self.prefix = prefix
        self.name = acc['acc']
        self.comm = acc['comm']
        self.stat = acc['stat']
        self.comm1 = acc['comm1']
        self.stat1 = acc['stat1']
        self.comm2 = acc['comm2']
        self.stat2 = acc['stat2']
        self.comm3 = acc['comm3']
        self.stat3 = acc['stat3']
        self.push = None
        statdb.create(self.name)
        if statdb.select(self.name) is None:
            statdb.insert(self.name, 0)


    def get_status(self, pause=.1):
        time.sleep(pause)
        stat = list(statdb.select(self.name).values())[0]
        out = (self.prefix+self.name+'-stat', stat)
        return out

    def event(self, top, msg):
        if top=="/iport/out":
            #try:
            if type(msg["events"]) is list:
                return self.handle(msg["events"][0], int(msg["eventtime"]))
            #except Exception as e:
            #    print('iPort ERR:', e)
        if top==self.prefix+self.name:
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)

class Short(Start):
    """ no homekit """
    def __init__(self, acc):
        super().__init__(acc)
        try:
            self.comm = self.comm.split('.')
        except Exception as e:
            print('iPort ERR:', e)

    def handle(self, msg, etime):
        #print('e', msg, msg['label'].replace(' ',''), self.stat, etime)
        if msg["label"].replace(' ', '') == self.stat:
            if msg["state"] == "1" and self.push is None:
                self.push = etime
            if msg["state"] == "0" and self.push is not None:
                if etime < self.push + 555:
                    self.push = None
                    stat = list(statdb.select(self.name).values())[0]
                    out, new = (), None
                    if stat == 0:
                        new = 1
                    if stat == 1:
                        new = 0
                    statdb.insert(self.name, new)
                    for comm in self.comm:
                        if comm[0] is "/":
                            out += (comm, new)
                        else:
                            out += ("/knx/in",'{"dstgad":"'+comm+'","value":"'+str(new)+'","dpt":"1"}')
                    return out
            if msg["state"] == "0" and etime >= self.push + 555:
                    self.push = None


class Scene(Short):

    def handle(self, msg, etime):
        if msg["label"].replace(' ','') == self.stat:
            if msg["state"] == "1" and self.push is None:
                self.push = etime
            if msg["state"] == "0" and self.push is not None:
                if etime < self.push + 666:
                    self.push = None
                    stat = list(statdb.select(self.name).values())[0]
                    out, val = (), None
                    if stat == 0:
                        val = str(self.comm1)
                        statdb.insert(self.name, 1)
                    if stat == 1:
                        val = str(self.stat1)
                        statdb.insert(self.name, 0)
                    for comm in self.comm:
                        if comm[0] is "/":
                            out += (comm, val)
                        else:
                            out += ("/knx/in",'{"dstgad":"'+comm+'","value":"'+val+'","dpt":"5"}')
                    return out
            if msg["state"] == "0" and etime >= self.push + 666:
                    self.push = None


class Switch(Short):

    def handle(self, msg, etime):
        if msg["label"].replace(' ','') == self.stat:
            if msg["state"] == "1" and self.push is None:
                self.push = etime
            if msg["state"] == "1" and self.push is not None:
                if etime >= self.push + 999:
                    self.push = etime
                    stat = list(statdb.select(self.name).values())[0]
                    if stat == 0:
                        statdb.insert(self.name, 1)
                        return (self.prefix+self.name+'-stat', 1)
                    if stat == 1:
                        statdb.insert(self.name, 0)
                        return (self.prefix+self.name+'-stat', 0)
            if msg["state"] == "0" and self.push is not None:
                self.push = None

