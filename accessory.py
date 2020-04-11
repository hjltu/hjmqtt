#!/usr/bin/env python3

"""
accessory.py

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
        statdb.create(self.name)
        if statdb.select(self.name) is None:
            statdb.insert(self.name, 0)
        if 'dimm' in self.name:
            statdb.create(self.name+'_dimm')
            if statdb.select(self.name+'_dimm') is None:
                statdb.insert(self.name+'_dimm', 0)
        if 'day' in self.stat2:
            statdb.create(self.name+'_day')
        if 'night' in self.stat3:
            statdb.create(self.name+'_nigth')

    def get_status(self, pause=.1):
        time.sleep(pause)
        stat = list(statdb.select(self.name).values())[0]
        out = (self.prefix+self.name+'-stat', stat)
        if 'dimm' in self.name and stat == 1:
            dimm = list(statdb.select(self.name+'_dimm').values())[0]
            out += (self.prefix+self.name+'-dimm', dimm)
        return out


class Rele(Start):

    def event(self, top, msg):
        if top==self.stat:
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)
        if top==self.prefix+self.name:
            return (self.comm, msg)


class Count(Start):

    def event(self, top, msg):
        if top==self.stat:
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)


class Electro(Start):
    """ 2-tariff electric counter """

    def __init__(self, acc, dimm=None, day='_day', night='_night'):
        super(Electro, self).__init__(acc, dimm=None, day='_day', night='_night')
        self.countNew = 0
        self.countOld = 0
        self.countDay = (statdb.select(self.prefix+self.name+"_day")).values()[0]
        self.countNight = (statdb.select(self.prefix+self.name+"_night")).values()[0]

    def event(self, top, msg, buf=100):
        if top=='/wemos'+wemos_name+'/out/'+wemos_pin:
            self.countNew = self.countNew + 1
            if self.countNew > self.countOld + buf:
                statdb.insert(self.name, msg)
                if self.tariff() == 1:
                    self.countDay = self.countDay+(self.countNew-self.countOld)
                    statdb.insert(self.name+"_day", self.countDay)
                if self.tariff() == 2:
                    self.countNight = self.countNight+(self.countNew-self.countOld)
                    statdb.insert(self.name+"_night", self.countNight)
                self.countOld = self.countNew
                #return (self.prefix+self.name+'-stat',msg)

    def tariff(self, t1=7, t2=23):
        h = dt.datetime.now().hour
        if h >= t1 and h < t2:
            return 1    # Day
        if h >= t2 or h < t1:
            return 2    # Night


class Short(Start):
    """ no homekit """
    def __init__(self, acc):
        super().__init__(acc)
        try:
            self.comm = self.comm.split('.')
        except:
            pass

    def event(self, top, msg):
        if top == self.stat and msg == 1:
            stat = list(statdb.select(self.name).values())[0]
            if stat==0:
                val=1
            if stat==1:
                val=0
            out=()
            statdb.insert(self.name, val)
            for comm in self.comm:
                if comm[0] == "/":
                    out+=(comm, val)
                else:
                    out += ("/knx/in",'{"dstgad":"'+comm+'","value":"'+str(val)+'","dpt":"1"}')
            return out

class Scene(Short):

    def event(self, top, msg):
        if top == self.stat and msg == 1:
            out, val = (), None
            stat = list(statdb.select(self.name).values())[0]
            if stat==0:
                statdb.insert(self.name, 1)
                val=self.comm1
            else:
                statdb.insert(self.name, 0)
                val=self.stat1
            for comm in self.comm:
                if comm[0] == "/":
                    out+=(comm, val)
                else:
                    out += ("/knx/in",'{"dstgad":"'+comm+'","value":"'+str(val)+'","dpt":"5"}')
            return out

class Switch(Start):

    def event(self, top, msg):
        if top == self.stat and msg == 2:
            stat = list(statdb.select(self.name).values())[0]
            if stat == 0:
                statdb.insert(self.name, 1)
                return (self.prefix+self.name+'-stat', 1)
            if stat == 1:
                statdb.insert(self.name, 0)
                return (self.prefix+self.name+'-stat', 0)
        if top==self.prefix+self.name:
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)

class Sensor(Start):

    """ Temp, Hum, Leak, Motion """

    def __init__(self, acc):
        super().__init__(acc)
        self.msg = None

    def event(self, top, msg):
        if top == self.stat:
            if self.msg != msg:
                self.msg = msg
                statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-curr', msg)


class NTC_Sensor(Start):

    """ for NTC 10kOhm thermistor, msg from analog input(ADC) """

    def __init__(self, name):
        super(NTC_Sensor, self).__init__(self.prefix+self.name)
        # list temperatures
        self.samples=[None]*8
        # NTC sensor resistance from ADC
        self.res=lambda x: 10000/(1025/x-1)
        # Temperature. Steinhart-Hart equation
        # B=?3430? for (-55..+125)
        # B=4141 for (-55..+155)
        self.temp=lambda b,y: 1/(1/298.3+math.log(self.res(y)/10000)/b)-273.3

    def my_temp(self,msg,B):
        if msg not in self.samples or None in self.samples:
            self.samples.pop()
            self.samples.insert(0,msg)
        try:
            sort = sorted(self.samples)
            while len(sort)>4:
                sort.pop()
                sort.pop(0)
            ma=sum(sort)/len(sort)
        except:
            return
        try:
            temp=self.temp(float(B),float(ma))
        except Exception as e:
            print("ERR:",str(e))
        return round(temp, 1)

    def event(acc,B,top,msg):
        if top=="/"+name+"/out/"+pin:
            temp=(self.my_temp(msg,B))
            if temp<150 and temp>-50:
                if self.db > temp+1 or self.db < temp-1:  # step one degree
                    self.db=temp
                    statdb.insert(self.name, temp)
                return (self.prefix+self.name+"-curr", temp)


class NTC_Term(Start):

    """ Thermoregulator for NTC thermistor
    inputs:
        curr: input device
        self.prefix+self.name: name
        name2,pin2: output device
        mode: 0-heating, 1-cooling """

    def event(self, top, msg, mode=0):
        if top == self.prefix+self.name+curr+"-curr":
            target = (statdb.select(self.name)).values[0]
            if type(target) is str:
                target = float(target)
            else:
                print("ERR:", self.prefix+self.name, "target", target)
                return
            if target<150 and target>-50:
                if float(msg)<target-0.5:
                    if mode==0:
                        out = ("/"+name2+"/in/"+pin2, 1)
                    if mode==1:
                        out = ("/"+name2+"/in/"+pin2, 0)
                    return out
                if float(msg)>target+0.5:
                    if mode==0:
                        out = ("/"+name2+"/in/"+pin2, 0)
                    if mode==1:
                        out = ("/"+name2+"/in/"+pin2, 1)
                    return out
        if top==self.prefix+self.name+'-target':
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)


class Term(Start):
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        statdb.create(self.name+'_target')
        statdb.create(self.name+'_mode')
        if statdb.select(self.name+'_target') is None:
            statdb.insert(self.name+'_target', 22)
        if statdb.select(self.name+'_mode') is None:
            statdb.insert(self.name+'_mode', 1)

    def get_status(self, pause=.1):
        time.sleep(pause)
        self.target = list(statdb.select(self.name+'_target').values())[0]
        self.mode = list(statdb.select(self.name+'_mode').values())[0]
        out = (self.prefix+self.name+'-target-stat', self.target)
        out += (self.prefix+self.name+'-mode-stat', self.mode)
        return out

    def event(self, top, msg):
        if top == self.stat:
            out = (self.prefix+self.name+'-curr', msg)
            if self.mode == 1:              # heatig
                if int(msg) < self.target:
                    out += (self.comm2, 1)
                if int(msg) >= self.target:
                    out += (self.comm2, 0)
            if self.mode == 2:              # cooling
                if int(msg) > self.target:
                    out += (self.comm3, 1)
                if int(msg) <= self.target:
                    out += (self.comm3, 0)
            return out
        if top==self.prefix+self.name+'-target':
            self.target = int(msg)
            statdb.insert(self.name+'_target', self.target)
            return (self.prefix+self.name+'-target-stat', self.target)
        if top==self.prefix+self.name+'-mode':
            out = ()
            if int(msg) == 1:
                self.mode = int(msg)
                out += (self.comm3, 0)
            if int(msg) == 2:
                self.mode = int(msg)
                out += (self.comm2, 0)
            if int(msg) == 0:
                self.mode = int(msg)
                out += (self.comm2, 0, self.comm3, 0)
            statdb.insert(self.name+'_mode', self.mode)
            out += (self.prefix+self.name+'-mode-stat', self.mode)
            return out

        # in use stat
        if top==self.stat2:     # heat
            return (self.prefix+self.name+'-use-stat', msg)
        if top==self.stat3:     # cool
            if float(msg) > 0:
                return (self.prefix+self.name+'-use-stat', 2)
            else:
                return (self.prefix+self.name+'-use-stat', 0)


class Dimmer(Start):
    def event(self, top, msg):
        if top == self.stat:
            if int(msg) == 0:
                statdb.insert( self.name, msg)
                return (self.prefix+self.name+'-stat',msg)
            if int(msg) > 0:
                statdb.insert(self.name, 1)
                statdb.insert(self.name+'_dimm', msg)
                return (self.prefix+self.name+'-stat',1,self.prefix+self.name+'-dimm-stat',msg)
        if top==self.prefix+self.name:
            if int(msg) == 0:
                return (self.comm, 0)
            if int(msg) == 1:
                time.sleep(.2)
                pwm = list(statdb.select(self.name+'_dimm').values())[0]
                if pwm == 0:
                    pwm = 255
                return (self.comm, pwm)
        if top==self.prefix+self.name+'-dimm':
            return (self.comm, int(float(msg)))


class Somfy(Start):
    def __init__(self, acc, prefix='/homekit/'):
        super().__init__(acc, prefix='/homekit/')
        statdb.create(self.name)
        if statdb.select(self.name) is None:
            statdb.insert(self.name, 0)

    def event(self, top, msg):
        if top == self.stat:
            msg = int(254./float(self.comm1)*float(msg))
            statdb.insert(self.name, msg)
            return (self.prefix+self.name+'-stat', msg)
        if top == self.prefix+self.name:
            msg = int(float(self.comm1)/254.*float(msg))
            return (self.comm, int(float(msg)))
