#! -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from parse import parse_filename, parse_logline_re, define_format
import os
import time
import datetime
from itertools import islice, groupby
from collections import deque
import re
import multiprocessing
import win32con
import win32evtlog
import win32evtlogutil
import winerror
import pywintypes
import threading
#import codecs
from operator import itemgetter as ig
import Queue
from buf_read import b_read

evt_dict={win32con.EVENTLOG_AUDIT_FAILURE:'AUDIT_FAILURE',
      win32con.EVENTLOG_AUDIT_SUCCESS:'AUDIT_SUCCESS',
      win32con.EVENTLOG_INFORMATION_TYPE:'INFORMATION',
      win32con.EVENTLOG_WARNING_TYPE:'WARNING',
      win32con.EVENTLOG_ERROR_TYPE:'ERROR'}

#error_flag = re.compile(r"^at")
dtre = re.compile(r"(\d{2})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})")
uc_re = re.compile(r"\u\w{4}")
descr_re = re.compile(r'''<The description for.+?:\s*u['"](.+)['"]\.>''', re.DOTALL)

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


class LogWorker(multiprocessing.Process):
    def __init__(self, in_q, out_q, c_q, stp, fltr):
        super(LogWorker,self).__init__()
        self.fltr = fltr
        self.stop = stp
        self.in_queue = in_q
        self.out_queue = out_q
        self.completed_queue = c_q

    def ret_self(self, l):
        return True

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
                if uc_re.search(l['msg']):
                    msg = l['msg'].decode('unicode-escape', 'replace')
                else:
                    msg = l['msg']
                ds = descr_re.search(msg)
                if ds:
                    msg = ds.group(1)
                self.out_queue.put((l['the_time'], l['computer'], l['logtype'], \
                    l['evt_type'], l['source'], msg, "#FFFFFF", False))
            self.completed_queue.put(1)

def datetime_intersect(t1start, t1end, t2start, t2end):
    return (t1start <= t2start and t2start <= t1end) or \
           (t2start <= t1start and t1start <= t2end)

def get_time(ed):
    return datetime.datetime(ed.tm_year,
                    ed.tm_mon,
                    ed.tm_mday,
                    ed.tm_hour,
                    ed.tm_min,
                    ed.tm_sec)

def queue_filler(evlogs, queue):
    for i in evlogs:
        queue.put(i)

def file_preparator(folders, fltr):
    #size = os.path.getsize
    flf = []
    for key, value in folders.iteritems():
        for f in os.listdir(key):
            fullf = os.path.join(key,f)
            pfn, ext = parse_filename(f)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt','log') and pfn in value:
                    flf.append([fullf, pfn])
    return flf

class FileLogWorker(multiprocessing.Process):
    def __init__(self, in_q, out_q, c_q, stp, fltr, formats):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_q
        self.out_queue = out_q
        self.stop = stp
        self.fltr = fltr
        self.completed_queue = c_q
        self.formats = formats

    def load(self):
        try:
            cdate = time.localtime(os.path.getctime(self.path))
        except WindowsError:
            print "WindowsError: %s" % self.path
            raise StopIteration
        if get_time(cdate)>self.fltr['date'][1]:
            raise StopIteration
        pformat = self.formats.get(self.Log, None)
        if not pformat:
            try:
                f = open(self.path, 'r')
            except IOError:
                print "IOError: %s" % self.path
                raise StopIteration
            line = True
            while line:
                line = f.readline()
                pformat = define_format(line)
                if pformat:
                    self.formats[self.Log] = pformat
                    break
        f.close()
        if not pformat:
            print "Not found the format for file %s" % self.path
            raise StopIteration
        at = [0,0]
        buff = []
        for string in b_read(self.path):
            if self.stop.is_set():
                break
            if "at" in string.startswith("at"):
                at[0]+=1
            if "Exception" in string:
                at[1]+=1
            parsed_s = parse_logline_re(string, cdate, pformat)
            if not parsed_s:
                buff.append(string)
            else:
                l_type = (at[0]>0 and at[1]>0) and "ERROR" or "?"
                buf.append(string)
                msg = "".join(reversed(buf))
                yield (parsed_s[0], "", self.Log, l_type , self.path, msg, "#FFFFFF", False)
                buf = []
                at = [0,0]

    def filter(self):
        def f_date(l):
            ndate = self.fltr['date']
            #try:
            if l[0]<ndate[0]:
                raise StopIteration
            #except TypeError:
            #    self.deq.clear()
            #    raise StopIteration
            return ndate[0]<=l[0]<=ndate[1]

        for l in (l1 for l1 in self.load() if f_date(l1)):
            yield l

    def group(self):
        for k, g in groupby(self.filter(), ig(0,1,2,3,4)):
            yield (k[0], k[1], k[2], k[3], k[4],\
                "".join(reversed([m[5] for m in g])),
                "#FFFFFF", False)

    def run(self):
        while 1:
            self.path, self.Log = self.in_queue.get()
            for l in self.group():
                self.out_queue.put(l)
            self.completed_queue.put(1)

class LogListFiller(threading.Thread):
    def __init__(self, q, model, view, stp, comp_q):#, pg):
        threading.Thread.__init__(self)
        self.queue = q
        self.model = model
        self.view = view
        self.c_q = comp_q
        self.stp = stp

    def run(self):
        self.view.freeze_child_notify()
        self.view.set_model(None)
        app = self.model.insert_after
        thr_ent = gtk.gdk.threads_enter
        thr_leave = gtk.gdk.threads_leave
        sib = None
        get = self.queue.get
        while 1:
            if self.stp.is_set():
                break
            try:
                l = get(True, 1)
                thr_ent()
                sib = app(sib,l)
                thr_leave()
            except Queue.Empty:
                pass
        get = self.queue.get_nowait
        while 1:
            try:
                l = get()
                thr_ent()
                sib=app(sib, l)
                thr_leave()
            except Queue.Empty:
                break
        self.model.set_sort_column_id(0 ,gtk.SORT_DESCENDING)
        self.view.set_model(self.model)
        self.view.thaw_child_notify()
        self.c_q.put(1)
