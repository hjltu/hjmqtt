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
"""


import statdb
import time
import myrgb


class Start:

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
        statdb.create(self.name)
        if statdb.select(self.name) is None:
            statdb.insert(self.name, 0)
        #if 'dimm' in self.name:
        #    statdb.create(self.name+'_dimm')
        #    if statdb.select(self.name+'_dimm') is None:
        #        statdb.insert(self.name+'_dimm', 0)
        #if 'rgb' in self.name:
        #    for color in 'rgb':
        #        statdb.create(self.name+'_'+color)
        #        if statdb.select(self.name+'_'+color) is None:
        #            statdb.insert(self.name+'_'+color, 0)

    def get_status(self, pause=.1):
        time.sleep(pause)
        stat = list(statdb.select(self.name).values())[0]
        out = (self.prefix+self.name+'-stat', stat)
        if 'dimm' in self.name and stat == 1:
            dimm = list(statdb.select(self.name+'_dimm').values())[0]
            out += (self.prefix+self.name+'-dimm', dimm)
        if 'rgb' in self.name and stat == 1:
            #self.r = list(statdb.select(self.name+'_r').values())[0]
            #self.g = list(statdb.select(self.name+'_g').values())[0]
            #self.b = list(statdb.select(self.name+'_b').values())[0]
            self.h, self.s, self.v = myrgb.rgb2hsv(self.r, self.g, self.b)
            out += (self.prefix+self.name+'-hue-stat', self.h)
            out += (self.prefix+self.name+'-sat-stat', self.s)
            out += (self.prefix+self.name+'-br-stat', self.v)
            print('hsv:', self.h, self.g, self.v)
        return out


class Rele(Start):

    def event(self, top, msg):
        if top=="/knx/out" and msg["dstgad"]==self.stat:
            statdb.insert(self.name, msg["value"])
            return (self.prefix+self.name+'-stat', msg["value"])
        if top==self.prefix+self.name:
            msg='{"dstgad":"'+self.comm+'","value":"'+str(msg)+'"}'
            return ("/knx/in",msg)


class Short(Start):
    """ no homekit """
    def __init__(self, acc):
        super().__init__(acc)
        try:
            self.comm = self.comm.split('.')
        except Exception as e:
            print('ERR: ',e)

    def event(self, top, msg):
        if top == "/knx/out" and msg['dstgad'] == self.stat:
            out = ()
            stat = msg["dstgad"]
            val = str(msg["value"])
            dpt = "1"
            try:
                if int(val)>2 and int(val)<256:
                    dpt = "5"
            except:
                    dpt = "9"
            for comm in self.comm:
                if comm[0] == "/":
                    out += (comm, int(val))
                else:
                    out += ("/knx/in",'{"dstgad":"'+comm+'","value":"'+val+'","dpt":"'+dpt+'"}')
            return out


class Scene(Short):
    """ no homekit, status: 0-1, comm: 0-255 (byte)
        0 - comm1, 1 - stat1 """

    def event(self, top, msg):
        if top == "/knx/out" and msg['dstgad'] == self.stat:
            out, val = (), None
            stat = msg["dstgad"]
            if msg["value"] == "0":
                val = str(self.comm1)
            if msg["value"] == "1":
                val = str(self.stat1)
            for comm in self.comm:
                if comm[0] == "/":
                    out += (comm, int(val))
                else:
                    out += ("/knx/in",'{"dstgad":"'+comm+'","value":"'+val+'","dpt":"5"}')
            return out


class Switch(Start):

    def event(self, top, msg):
        if top == "/knx/out" and msg['dstgad'] == self.stat:
            val = str(msg["value"])
            statdb.insert(self.name, val)
            return (self.prefix+self.name+'-stat', val)
        if top == self.prefix+self.name:
            statdb.insert(self.name, msg)
            out = (self.prefix+self.name+'-stat', msg)
            out = ("/knx/in",'{"dstgad":"'+self.comm+'","value":"'+str(msg)+'","dpt":"1"}')
            return out


class Switch_NC(Start):
    """
    NC - no command, status only
    use Short instead of it
    """
    def event(self,homekit,stat,top,msg):
        if top=="/knx/out" and msg["dstgad"]==stat:
            statdb.update("stat",homekit,msg["value"])
            return ('/homekit/'+homekit+'-stat',msg["value"])


class Sensor(Start):

    """ Temp, Hum, Leak, Motion """

    def event(self,top,msg):
        if top=="/knx/out" and msg["dstgad"]==self.stat:
            stat = list(statdb.select(self.name).values())[0]
            if stat != msg['value']:
                statdb.insert(self.name, msg["value"])
            return (self.prefix+self.name+'-curr', msg["value"])


class Term(Start):

    """ temp regulator
    curr: knx temperature,
    target: knx target temp,
    stat: knx target status
    """
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        statdb.create(self.name+'_target')
        statdb.create(self.name+'_mode')
        if statdb.select(self.name+'_target') is None:
            statdb.insert(self.name+'_target', 22)
        if statdb.select(self.name+'_mode') is None:
            statdb.insert(self.name+'_mode', 1)

    def get_status(self, pause=.1):
        super().get_status(pause=.1)
        self.target = list(statdb.select(self.name+'_target').values())[0] or 10
        self.mode = list(statdb.select(self.name+'_mode').values())[0] or 1
        out = (self.prefix+self.name+'-target-stat', self.target)
        out += (self.prefix+self.name+'-mode-stat', self.mode)
        return out

    def event(self,top,msg):
        # current
        if top=="/knx/out" and msg["dstgad"] == self.stat:
            out = (self.prefix+self.name+'-curr',msg["value"])
            return out
        # target
        if top == "/knx/out" and msg["dstgad"] == self.stat1:
            if float(msg['value']) != self.target:
                self.target = float(msg['value'])
                statdb.insert(self.name+'_target', self.target)
            out = (self.prefix+self.name+"-target-stat", self.target)
            return out
        if top == self.prefix+self.name+'-target':
            if float(msg) != self.target:
                self.target = float(msg)
                statdb.insert(self.name+'_target', self.target)
                out = ("/knx/in",'{"dstgad":"'+self.comm1+'","dpt": "9", "value":"'+str(self.target)+'"}')
                return out
        # mode
        if top == self.prefix+self.name+'-mode':
            if float(msg) != self.mode:
                self.mode = float(msg)
                statdb.insert(self.name+'_mode', self.mode)
            out = (self.prefix+self.name+'-mode-stat', msg)
            if self.mode == 1:
                out += ("/knx/in",'{"dstgad":"'+self.comm+'","value":"1"}')
            if self.mode == 2:
                out += ("/knx/in",'{"dstgad":"'+self.comm+'","value":"0"}')
            return out
        # in use
        if top == "/knx/out" and msg["dstgad"] == self.stat2:   # heat
            return (self.prefix+self.name+'-use-stat', msg['value'])
        if top == "/knx/out" and msg["dstgad"] == self.stat3:   # cool
            if float(msg["value"]) > 0:
                return (self.prefix+self.name+'-use-stat', 2)
            else:
                return (self.prefix+self.name+'-use-stat', 0)


class Term_My(Start):
    """ my temp regulator
    curr: knx temperature,
    rele: knx rele,
    stat: knx rele status
    """
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        if 'term' in self.name:
            statdb.create(self.name+'_target')
            statdb.create(self.name+'_mode')

    def event(self, top, msg):
        if top=="/knx/out" and msg["dstgad"]==curr:
            out=('/homekit/'+homekit+'-curr',msg["value"])
            target=float(statdb.select('stat',homekit))
            if target<10:
                statdb.update('stat',homekit,10)
                out+=('/homekit/'+homekit+'-stat',10)
            if float(msg["value"])<target:
                out+=("/knx/in",'{"dstgad":"'+rele+'","value":1}')
                out+=("/homekit/"+homekit+"-mode-stat",1)
            if float(msg["value"])>target:
                out+=("/knx/in",'{"dstgad":"'+rele+'","value":0}')
                out+=("/homekit/"+homekit+"-mode-stat",0)
            return out
        if top=='/homekit/'+homekit+'-target':
            statdb.update('stat',homekit,msg)
            out=('/homekit/'+homekit+'-stat',msg)
            return out


class Dimmer(Start):
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        if 'dimm' in self.name:
            statdb.create(self.name+'_dimm')
            if statdb.select(self.name+'_dimm') is None:
                statdb.insert(self.name+'_dimm', 0)

    def event(self, top, msg):
        if top=="/knx/out" and msg["dstgad"]==self.stat:
            if float(msg["value"])==0:
                statdb.insert(self.name, msg["value"])
                return (self.prefix+self.name+'-stat',0)
            if float(msg["value"])>0:
                statdb.insert(self.name, 1)
                statdb.insert(self.name+'_dimm',msg["value"])
                return (self.prefix+self.name+'-stat', 1, self.prefix+self.name+'-dimm-stat',msg["value"])
        if top == self.prefix+self.name:
            if float(msg)==0:
                return ("/knx/in",'{"dstgad":"'+self.comm+'","value":"0","dpt":"5"}')
            if float(msg)==1:
                time.sleep(.2)
                pwm = list(statdb.select(self.name+'_dimm').values())[0]
                if float(pwm)==0:
                    pwm=255
                return ("/knx/in",'{"dstgad":"'+self.comm+'","value":"'+str(pwm)+'","dpt":"5"}')
        if top==self.prefix+self.name+'-dimm':
            return ("/knx/in",'{"dstgad":"'+self.comm+'","value":"'+str(msg)+'","dpt":"5"}')


class Dimmer_NS(Start):
    """
    NS - no status from KNX
    """
    def event(self,homekit,dimm,stat,top,msg):
        if top=='/homekit/'+homekit:
            if float(msg)==0:
                return ("/knx/in",'{"dstgad":"'+dimm+'","value":"0","dpt":"5"}','/homekit/'+homekit+'-stat',0)
            if float(msg)==1:
                time.sleep(.2)
                pwm=statdb.select('stat',homekit+'-dimm')
                if float(pwm)==0:
                    pwm=255
                return ("/knx/in",'{"dstgad":"'+dimm+'","value":"'+str(pwm)+'","dpt":"5"}','/homekit/'+homekit+'-stat',1,'/homekit/'+homekit+'-dimm-stat',pwm)
        if top=='/homekit/'+homekit+'-dimm':
            statdb.update('stat',homekit+'-dimm',msg)
            return ("/knx/in",'{"dstgad":"'+dimm+'","value":"'+str(msg)+'","dpt":"5"}')


class Dimmer_RGB(Start):
    """
    RGB: on/off or 3 comm/stat
    arlight KNX-104-dim-suf
    """
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        if 'rgb' in self.name:
            for color in 'rgb':
                statdb.create(self.name+'_'+color)
                if statdb.select(self.name+'_'+color) is None:
                    statdb.insert(self.name+'_'+color, 0)
        self.r = list(statdb.select(self.name+'_r').values())[0]
        self.g = list(statdb.select(self.name+'_g').values())[0]
        self.b = list(statdb.select(self.name+'_b').values())[0]
        self.h, self.s, self.v = myrgb.hsv2rgb(self.r, self.g, self.b)
        print('rgb stat:', self.r, self.g, self.b)

    def event(self, top, msg):
        if top=='/knx/out' and (msg["dstgad"] == self.stat1 or
                msg["dstgad"] == self.stat2 or
                msg["dstgad"] == self.stat3) and float(msg["value"]) > 0:
            if msg["dstgad"] == self.stat1:
                self.r = msg['value']
                statdb.insert(self.name+'_r', self.r)
            if msg["dstgad"] == self.stat2:
                self.g = msg['value']
                statdb.insert(self.name+'_g', self.g)
            if msg["dstgad"] == self.stat3:
                self.b = msg['value']
                statdb.insert(self.name+'_b', self.b)
            self.h, self.s, self.v = myrgb.rgb2hsv(self.r, self.g, self.b)
            print('hsv:', self.h, self.s, self.v)
            out = (self.prefix+self.name+'-hue-stat', self.h)
            out += (self.prefix+self.name+'-sat-stat', self.s)
            out += (self.prefix+self.name+'-br-stat', self.v)
            return out
        if top == self.prefix+self.name+'-RGB':
            if msg == '#000000':
                print('RGB off:', self.name, msg, type(msg))
                statdb.insert(self.name, 0)
                out = (self.prefix+self.name+'-stat', 0)
                out += ("/knx/in",'{"dstgad":"'+self.comm+'","value":"0"}')
                return out
            else:
                statdb.insert(self.name, 1)
                out = (self.prefix+self.name+'-stat', 1)
                return out
            # self.r, self.g, self.b = myrgb.hsv2rgb()
        if top == self.prefix+self.name:
            if float(msg)==0:
                # TODO byte commands
                return ("/knx/in",'{"dstgad":"'+self.comm+'","value":"0"}')
            if float(msg)==1:
            #    time.sleep(.2)
                return self.to_knx()
        if top==self.prefix+self.name+'-br':
            self.v = float(msg)
            self.r, self.g, self.b = myrgb.hsv2rgb(self.h, self.s, self.v)
            return self.to_knx()
            #return ("/knx/in",'{"dstgad":"'+self.comm+'","value":"'+str(msg)+'","dpt":"5"}')
        if top==self.prefix+self.name+'-hue':
            self.h = float(msg)
            print('rgb:', self.r, self.g, self.b)
        if top==self.prefix+self.name+'-sat':
            time.sleep(.1)
            self.s = float(msg)
            self.r, self.g, self.b = myrgb.hsv2rgb(self.h, self.s, self.v)
            return self.to_knx()

    def to_knx(self):
        print('rgb:', self.r, self.g, self.b)
        out = ("/knx/in",'{"dstgad":"'+self.comm1+'","value":"'+str(self.r)+'","dpt":"5"}')
        out += ("/knx/in",'{"dstgad":"'+self.comm2+'","value":"'+str(self.g)+'","dpt":"5"}')
        out += ("/knx/in",'{"dstgad":"'+self.comm3+'","value":"'+str(self.b)+'","dpt":"5"}')
        return out

class Somfy(Start):
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        statdb.create(self.name)
        if statdb.select(self.name) is None:
            statdb.insert(self.name, 0)

    def event(self, top, msg):
        if top=="/knx/out" and msg["dstgad"]==self.stat:
            #statdb.insert(self.name, msg["value"])
            #msg = int(254./float(msg["value"])*float(msg))
            msg = float(msg["value"])
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)
        if top == self.prefix+self.name:
            #msg = int(float(self.comm1)/254.*float(msg))
            msg='{"dstgad":"'+self.comm+'","value":"'+str(msg)+'","dpt":"5"}'
            return ("/knx/in",msg)
