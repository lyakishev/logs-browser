#! -*- coding: utf8 -*-

from parse import parse_filename, parse_logline_re, define_format
import os
import time
import datetime
from collections import deque
from buf_read import mmap_block_read

def get_time(tm_dt):
    return datetime.datetime(tm_dt.tm_year,
                    tm_dt.tm_mon,
                    tm_dt.tm_mday,
                    tm_dt.tm_hour,
                    tm_dt.tm_min,
                    tm_dt.tm_sec)


def file_preparator(folders):
    flf = []
    for key, value in folders.iteritems():
        for file_ in os.listdir(key):
            fullf = os.path.join(key, file_)
            pfn, ext = parse_filename(file_)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt', 'log') and pfn in value:
                flf.append([fullf, pfn])
    return flf

def filelogworker(dates, path, log):
        try:
            cdate = time.localtime(os.path.getctime(path))
        except WindowsError:
            #print "WindowsError: %s" % path
            raise StopIteration
        if get_time(cdate) > dates[1]:
            raise StopIteration
        try:
            file_ = open(path, 'r')
        except IOError:
            raise StopIteration
        for line in file_:
            pformat = define_format(line)
            if pformat:
                break
        file_.close()
        try:
            if not pformat:
                #print "Not found format for file %s" % path
                raise StopIteration
        except UnboundLocalError:
            raise StopIteration
        buff = deque()
        for string in mmap_block_read(path, 16*1024):
            parsed_s = parse_logline_re(string, cdate, pformat)
            if not parsed_s:
                buff.appendleft(string)
            else:
                date = parsed_s[0]
                if date < dates[0]:
                    return
                if date <= dates[1]:
                    buff.appendleft(string)
                    msg = "".join(buff)
                    yield (date,
                           "",
                           log,
                           "ERROR" if ("Exception" in msg and "  at " in msg) \
                                   else "?",
                           path,
                           msg)
                buff.clear()

if __name__ == "__main__":
    def test(dates,path,log,block,im):
        for i in filelogworker(dates,path,log,block,im):
            i
    #import pstats
    #import cProfile
    dates=(datetime.datetime.min,
           datetime.datetime.max)
    #path = "/home/user/sharew7/logs/log/20101206_FORIS.TelCRM.Interfaces.OTCP.Log"
    log = "FORIS.TelCRM.Interfaces.RD.Log"
    import sqlite3
    conn = sqlite3.connect("bench.db")
    c = conn.cursor()
    c.execute("create table bench_mmap (path text, block_size int,logs int, time real);")
    conn.commit()
    for root,dirs,files in os.walk("/home/user/sharew7/logs/log/"):
        for file_ in files:
            fullf = os.path.join(root,file_)
            print fullf
            for b in map(lambda x: x*1024, map(lambda x: 2**x, range(11))):
                for i in range(1,100):
                    dt = time.time()
                    test(dates,fullf,log,b, i)
                    time_ = time.time() - dt
                    c.execute("insert into bench_mmap values(?,?,?,?);", (fullf,b,
                                                            i,time_))
    conn.commit()
    c.close()
    conn.close()


    #cProfile.runctx("test()",
    #                 globals(), locals(), "flw")
    #p = pstats.Stats('flw')
    #p.strip_dirs().sort_stats(-1).print_stats()

    
