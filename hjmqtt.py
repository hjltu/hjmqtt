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


import os,sys,time,datetime
import _thread,threading
import json
import config

try:
    import paho.mqtt.client as mqtt
except:
    print('paho-mqtt Err!')
    sys.exit(1)
import statdb, csv2list
import accessory, accessoryknx, accessoryiport


VERSION="4-aug-19"
SERIAL = config.SERIAL

""" create accessories
"""
csv_file = os.environ['HOME']+'/'+SERIAL+'.csv'
acc_list = csv2list.main(csv_file)
#print(type(acc_list))
if type(acc_list) is not list:
    csv_file = os.environ['HOME']+'/file.csv'
    acc_list = csv2list.main(csv_file)

acc_obj = []
for acc in acc_list:
    if acc['sys'] == 'homekit':
        continue
    if acc['sys'] == 'knx':
        if (acc['type'] == 'lamp' or
                acc['type'] == 'fan' or
                acc['type'] == 'outlet'):
            obj = accessoryknx.Rele(acc)
        if acc['type'] == 'dimm_lamp':
            obj = accessoryknx.Dimmer(acc)
        if acc['type'] == 'rgb_lamp':
            obj = accessoryknx.Dimmer_RGB(acc)
        if (acc['type'] == 'temp' or
                acc['type'] == 'motion' or
                acc['type'] == 'leak' or
                acc['type'] == 'hum'):
            obj = accessoryknx.Sensor(acc)
        if acc['type'] == 'term':
            obj = accessoryknx.Term(acc)
        if acc['type'] == 'blinds':
            obj = accessoryknx.Somfy(acc)
        if acc['type'] == 'switch':
            obj = accessoryknx.Switch(acc)
        if acc['type'] == 'short':
            obj = accessoryknx.Short(acc)
        if acc['type'] == 'scene':
            obj = accessoryknx.Scene(acc)

    if acc['sys'] == 'mqtt':
        if (acc['type'] == 'lamp' or
                acc['type'] == 'fan' or
                acc['type'] == 'outlet'):
            obj = accessory.Rele(acc)
        if acc['type'] == 'switch':
            obj = accessory.Switch(acc)
        if acc['type'] == 'short':
            obj = accessory.Short(acc)
        if acc['type'] == 'scene':
            obj = accessory.Scene(acc)
        if acc['type'] == 'dimm_lamp':
            obj = accessory.Dimmer(acc)
        if acc['type'] == 'temp':
            obj = accessory.Sensor(acc)
        if acc['type'] == 'hum':
            obj = accessory.Sensor(acc)
        if acc['type'] == 'leak':
            obj = accessory.Sensor(acc)
        if acc['type'] == 'motion':
            obj = accessory.Sensor(acc)
        if acc['type'] == 'term':
            obj = accessory.Term(acc)
        if acc['type'] == 'blinds':
            obj = accessory.Somfy(acc)

    if acc['sys'] == 'iport':
        if acc['type'] == 'short':
            obj = accessoryiport.Short(acc)
        if acc['type'] == 'scene':
            obj = accessoryiport.Scene(acc)
        if acc['type'] == 'switch':
            obj = accessoryiport.Switch(acc)

    acc_obj.append(obj)

print('len', len(acc_obj))


def cleanJson(msg):
    return json.dumps(msg)#.replace("\n", "")

def my_exit(err):   # exit programm
    os._exit(err)
    os.kill(os.getpid)

def my_publish(top=None,msg=None):
    #print "top =",top," msg =",msg
    if top is None:
        return
    if msg is None:
        if type(top) is tuple and len(top)>1:
            topic=top
            #print "check:",topic
            try:
                for i in range(0,len(topic),2):
                    print("pub:",topic[i],topic[i+1],"\t\t",time.ctime())
                    client.publish(topic[i],topic[i+1])
                return
            except Exception as e:
                print('publish error: {0}'.format(e))
        else:
            return
    try:
        client.publish(top,msg)
    except Exception as e:
        print('publish exception: {0}'.format(e))

def my_stat():

    """
    receive status from database
    """
    #global acc_obj
    for acc in acc_obj:
        #print(acc.__class__.__name__,dir(acc))
        my_publish(acc.get_status())

def my_start():
    """
    loop thread
    """
    time.sleep(1)
    my_stat()
    th=threading.Timer(3600*10,my_start)
    th.daemon=True
    th.start()



def my_event(top,msg):

    """ new thread for handle mqtt event
    """

    print("event:",top, msg.decode(), "\t\t",time.ctime())

    # if wemos start
    if '/wemos' and '/out/start' in top and msg=='start':
        c=''
        for i in top:
            if i.isdigit():
                c+=i
        my_publish('/wemos'+c+'/in/test','test')

    # homeassistant start
    if "/hass/" in top and msg=="start":
        my_stat()

    # KNX baos json
    try:
        if type(msg) is bytes:
            j=msg.decode()
            j = json.loads(j)
            msg=j
    except Exception as e:
        msg = msg.decode("utf-8")
        #print("ERR: msg2json",e)

    for acc in acc_obj:
        my_publish(acc.event(top, msg))


def on_connect(client, userdata, flags, rc):
    print("OK Connected with result code "+str(rc), time.ctime())
    client.subscribe("/#")

def on_message(client, userdata, msg):
    if msg.topic == '/paho/in':
        my_publish('/paho/out',msg.payload)
    if msg.topic == '/paho/in' and msg.payload == "stop":
        client.disconnect()

    if threading.active_count()<10:
        ev=threading.Thread(target=my_event, args=(msg.topic,msg.payload))
        ev.daemon=True
        ev.start()
        #print msg.topic,':',msg.payload,', thread:',threading.active_count(),
        #print ', date:',datetime.datetime.now()

def usage():
    print(__doc__)

client = mqtt.Client()
#client.connect("192.168.0.10",1883,3600)
client.connect("localhost",1883,3600)
#client.connect("192.168.1.2",1883,60)
client.publish("/paho/out", 'start');
client.on_connect = on_connect
client.on_message = on_message

print(__name__,VERSION)
_thread.start_new_thread(my_start,())
try:
    client.loop_forever()
except KeyboardInterrupt:
    pass
