#!/usr/bin/python
# -*- coding: utf-8 -*- 

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

usage: python3 send-mail.py email@address

crontab:
1 5 1 * * cd /home/pi/hjmqtt && python3 send-mail.py email@address
"""

import smtplib
import sys
import time
from email.mime.text import MIMEText
import statdb


MAIL = "email"
PASS = "email password"
SMTP_SRV = "SMTP server"
SMTP_PORT = "SMTP port"

# divide for electro counter
divEl = 3200	# imp/kW*h
# divide for water counter
divWt = 100		# 0.01 m3


def main(arg):

    # get counters
    EL=statdb.select("stat", "electro1")
    ELD=statdb.select("stat", "electro1-day")
    ELN=statdb.select("stat", "electro1-night")
    WHOT=statdb.select("stat", "water1")
    WCOLD=statdb.select("stat", "water2")

    # actual value = count / divide + shift
    EL=float(EL)/divEl + 0
    ELD=float(ELD)/divEl + 0
    ELN=float(ELN)/divEl + 0
    diff = (EL - (ELD + ELN))/3
    ELD += diff*2   # correct Day
    ELN += diff     # correct Night
    WHOT=float(WHOT)/divWt + 0
    WCOLD=float(WCOLD)/divWt + 0

    text = "Ф.И.О <br>\
    Адрес: <br>\n\
    Договор(л/с) № <br>\
        Электроэнергия: <br>\
    Общее: {} kW*h <br>\
    День: {} kW*h <br>\
    Ночь: {} kW*h <br>\
        Вода: <br>\
    Горячая: {} m3 <br>\
    Холодная: {} m3 \
    ".format(round(EL,2), round(ELD,2), round(ELN,2), round(WHOT,2), round(WCOLD,2))

    #print(text)
    msg = MIMEText(text, "plain")
    msg['Subject'] = "Показания приборов учета"
    msg['From'] = MAIL
    msg['Content-Type'] = 'text/html; charset=UTF-8'

    server = smtplib.SMTP_SSL(SMTP_SRV, SMTP_SRV)
    #server.set_debuglevel(1)
    #server.ehlo()
    #server.starttls()
    #server.ehlo()
    server.login(MAIL, PASS)
    #server.auth_plain()
    try:
        for to in arg:
            print("send to:", to)
            msg['To'] = to
            server.sendmail(MAIL, to, msg.as_string())
            time.sleep(1)
    except Exception as e:
        print("ERR",str(e))
    #server.rset()
    server.quit()

if(__name__=='__main__'):
    main(sys.argv[1:])
