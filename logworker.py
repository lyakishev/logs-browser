#! -*- coding: utf8 -*-

from evs import *
import threading
import pygtk
pygtk.require("2.0")
import gtk, gobject
from parse import parse_filename, parse_logline
from pyparsing import ParseException
import os
import time
import datetime
from itertools import ifilter, islice
import Queue
from itertools import groupby
from collections import deque
import re
import multiprocessing
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import pywintypes
import threading

evt_dict={win32con.EVENTLOG_AUDIT_FAILURE:'AUDIT_FAILURE',
      win32con.EVENTLOG_AUDIT_SUCCESS:'AUDIT_SUCCESS',
      win32con.EVENTLOG_INFORMATION_TYPE:'INFORMATION',
      win32con.EVENTLOG_WARNING_TYPE:'WARNING',
      win32con.EVENTLOG_ERROR_TYPE:'ERROR'}

error_flag = re.compile(r"^at")
dtre = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")

def getEventLog(ev_obj, server, logtype):
    log = {}
    the_time = ev_obj.TimeGenerated.Format() #'12/23/99 15:54:09'
    sdt = dtre.search(the_time)
    #strptime has problem with threads
    #dtdate = datetime.datetime.strptime(the_time, '%m/%d/%y %H:%M:%S') #
    dtdate = datetime.datetime(int("20"+sdt.group(3)), int(sdt.group(1)),
                                int(sdt.group(2)), int(sdt.group(4)),
                                int(sdt.group(5)),int(sdt.group(6)))
    log['evt_id'] = str(winerror.HRESULT_CODE(ev_obj.EventID))
    log['computer'] = str(ev_obj.ComputerName)
    log['cat'] = ev_obj.EventCategory
    log['record'] = ev_obj.RecordNumber
    log['msg'] = str(win32evtlogutil.SafeFormatMessage(ev_obj, logtype))
    log['logtype'] = logtype
    log['server'] = server
    log['source'] = str(ev_obj.SourceName)
    if not ev_obj.EventType in evt_dict.keys():
	log['evt_type'] = "unknown"
    else:
	log['evt_type'] = str(evt_dict[ev_obj.EventType])
    log['the_time'] = dtdate
    return log


class LogWorker(threading.Thread):
    def __init__(self, in_q, out_q, c_q, stp, fltr):
        super(LogWorker,self).__init__()
        self.ret_self = lambda l: True
        self.fltr = fltr
        self.stop = stp
        self.in_queue = in_q
        self.out_queue = out_q
        self.completed_queue = c_q

    def f_date(self, l):
        if l['the_time']<self.fltr['date'][0]:
            raise StopIteration
        return (l['the_time']<=self.fltr['date'][1] and \
            l['the_time']>=self.fltr['date'][0])

    def f_likecont(self, l):
         return (eval(self.fltr['content'][0]))# in l['msg']:

    def f_notlikecont(self, l):
        return (self.fltr['content'][1] not in l['msg'])

    def f_type(self, l):
        return (l['evt_type'] in self.fltr['types'])

    def load(self):
        try:
            hand = win32evtlog.OpenEventLog(self.server, self.logtype)  #!!!!!!
        except pywintypes.error:
            print "Error: %s %s" % (self.server, self.logtype)
            return
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
        while 1:
            if self.stop.is_set():
                break
            while 1:
                try:
                    events=win32evtlog.ReadEventLog(hand,flags,0)
                except pywintypes.error:
                    print "Pause %s %s" % (self.server, self.logtype)
                    hand.Detach() #need?
                    time.sleep(1)
                    hand = win32evtlog.OpenEventLog(self.server, self.logtype)  #!!!!!!
                else:
                    break
            if events:
                    for ev_obj in events:
                        if self.stop.is_set():
                            break
                        yield getEventLog(ev_obj, self.server, self.logtype)
            else:
                    try:
                        win32evtlog.CloseEventLog(hand)
                    except pywintypes.error:
                        print "Can't close"
                    finally:
                        return
    def filter(self):
        self.type_func = self.fltr['types'] and self.f_type or self.ret_self
        self.date_func = self.fltr['date'] and self.f_date or self.ret_self
        self.content_like_func = self.fltr['content'][0] and self.f_likecont or self.ret_self
        self.content_notlike_func = self.fltr['content'][1] and self.f_notlikecont or self.ret_self
        self.f1 = (l for l in self.load() if self.date_func(l))
        self.f2 = (l for l in self.f1 if self.type_func(l))
        self.f3 = (l2 for l2 in (l1 for l1 in self.f2 if self.content_like_func(l1)) if self.content_notlike_func(l2))
        self.f4 = islice(self.f3, 0, self.fltr['last'] and self.fltr['last'] or None)
        for l in self.f4:
            yield l

    def run(self):
        while 1:
            self.server, self.logtype = self.in_queue.get()
            for l in self.filter():
                self.out_queue.put((l['the_time'], l['computer'], l['logtype'], \
                    l['evt_type'], l['source'], l['msg'].decode('unicode-escape'), "#FFFFFF"))
            self.completed_queue.put(1)

def datetime_intersect(t1start, t1end, t2start, t2end):
    return (t1start <= t2start and t2start <= t1end) or \
           (t2start <= t1start and t1start <= t2end)

def get_m_time(path, cdate):
    deq = deque()
    f = open(path, 'r')
    deq.extend(f.readlines())
    f.close()
    while deq:
        string = deq.pop()
        parsed_s = parse_logline(string,cdate)
        if parsed_s:
            return parsed_s[0]
    ed = cdate
    return datetime.datetime(ed.tm_year,
                    ed.tm_mon,
                    ed.tm_mday,
                    ed.tm_hour,
                    ed.tm_min,
                    ed.tm_sec)

def evl_preparator(evlogs, queue):
    for i in evlogs:
        queue.put(i)

def file_preparator(folders, fltr, queue):
    ltime = time.localtime
    for key, value in folders.iteritems():
        for f in os.listdir(key):
            fullf = os.path.join(key,f)
            if os.path.isfile(fullf):
                pfn, ext = parse_filename(f)
                if pfn in value and ext in ('txt','log'):
                    f_end_date = get_m_time(fullf, \
                        ltime(os.path.getmtime(fullf)))
                    sd = ltime(os.path.getctime(fullf))
                    f_start_date = datetime.datetime(sd.tm_year,
                        sd.tm_mon,
                        sd.tm_mday,
                        sd.tm_hour,
                        sd.tm_min,
                        sd.tm_sec)
                    if datetime_intersect(fltr['date'][0],
                                            fltr['date'][1],
                                            f_start_date, f_end_date):
                        queue.put(fullf)


class FileLogWorker(multiprocessing.Process):
    def __init__(self, in_q, out_q, c_q, stp, fltr):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_q
        self.out_queue = out_q
        self.deq = deque()
        self.buf_deq = deque()
        self.stop = stp
        self.fltr = fltr
        self.completed_queue = c_q

    def load(self):
        cdate = time.localtime(os.path.getctime(self.path))
        f = open(self.path, 'r')
        self.deq.extend(f.readlines())
        f.close()
        at = [0,0]
        while self.deq:
            if self.stop.is_set():
                self.deq.clear()
                self.buf_deq.clear()
                break
            string = self.deq.pop()
            if error_flag.search(string.strip()):
                at[0]+=1
            if "Exception" in string:
                at[1]+=1
            parsed_s = parse_logline(string, cdate)
            if not parsed_s:
                self.buf_deq.appendleft(string)
            else:
                l_type = (at[0]>0 and at[1]>0) and "ERROR" or "?"
                at[0]=0
                at[1]=0
                self.buf_deq.appendleft(parsed_s[1])
                msg = "".join(self.buf_deq)
                self.buf_deq.clear()
                yield (parsed_s[0], "", "", l_type , self.path, msg, "#FFFFFF")

    def filter(self):
        def f_date(l):
            try:
                if l[0]<self.fltr['date'][0]:
                    self.deq.clear()
                    raise StopIteration
            except TypeError:
                self.deq.clear()
                raise StopIteration
            return (l[0]<=self.fltr['date'][1] and \
                l[0]>=self.fltr['date'][0])

        for l in (l1 for l1 in self.load() if f_date(l1)):
            yield l

    def group(self):
        for k, g in groupby(self.filter(), lambda x: [x[0],x[1],x[2],x[3],x[4]]):
            yield (k[0], k[1], k[2], k[3], k[4],\
                "".join(reversed([m[5] for m in g])),
                "#FFFFFF")


    def run(self):
        while 1:
            self.path = self.in_queue.get()
            for l in self.group():
                self.out_queue.put(l)
            self.completed_queue.put(1)

class LogListFiller(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.queue = q

    def run(self):
        while 1:
            l = self.queue.get()
            gtk.gdk.threads_enter()
            self.model.append(l)
            gtk.gdk.threads_leave()


