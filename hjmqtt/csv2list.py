#!/usr/bin/env python3

"""
csv2list.py
hjltu@ya.ru
29-jul19

task: csv to list

usage:
    ./csv2list.py my.csv
"""

import sys
import csv


def check_csv_to_not_ascii(csvfile):
    return
    isascii = lambda s: len(s) == len(s.encode())
    with open(csvfile, 'r') as f:
        data = f.read()
        return isascii(data)


def remove_whitespaces_from_list(row):
    out = []
    for r in row:
        l = r.replace(' ','')
        ll = l.replace("\\",'')
        out.append(ll)
    return out


def read_csv(csvfile):
    try:
        with open(csvfile, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            return csv_to_list_of_dicts(reader)
    except:
        return "ERR read csv's"


def csv_to_list_of_dicts(reader):
    l=[]
    line=0
    d={}
    for row in reader:
        if row:
            row = remove_whitespaces_from_list(row)
            if '#' not in row[0]:
                if line is 0:
                    col = row
                else:
                    try:
                        d = dict(zip(col, row))
                        d["acc"] = d["sys"] + '_' + d["type"] + str(line)
                        l.append(d)
                    except:
                        print('ERR:', row)
                line += 1
    print(l)
    return l


def main(csvfile):
    if check_csv_to_not_ascii(csvfile) is False:
        return "ERR not ascii string"
    return read_csv(csvfile)


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as e:
        print(e)
