from evs import *
import threading
import pygtk
pygtk.require("2.0")
import gtk, gobject
from parse import filename, file_log
from pyparsing import ParseException
import os
import time
import datetime
from itertools import ifilter, islice
import Queue
from itertools import groupby
from collections import deque
import re

max_connections = 5
semaphore = threading.BoundedSemaphore(value=max_connections)
lock = threading.Lock()

error_flag = re.compile(r"^at")


class LogWorker(threading.Thread):
    def __init__(self, comp, log, fltr, model, progress, frac, sens_list, evt):
        threading.Thread.__init__(self)
        self.ret_self = lambda l: True
        self.comp = comp
        self.log = log
        self.fltr = fltr
        self.model = model
        self.progress = progress
        self.frac = frac
        self.sens_list = sens_list
        self.evt = evt
        self.type_func = self.fltr['types'] and self.f_type or self.ret_self
        self.date_func = fltr['date'] and self.f_date or self.ret_self
        self.content_like_func = fltr['content'][0] and self.f_likecont or self.ret_self
        self.content_notlike_func = fltr['content'][1] and self.f_notlikecont or self.ret_self
        self.f1 = (l for l in getEventLogs(self.comp, self.log) if self.date_func(l))
        self.f2 = (l for l in self.f1 if self.type_func(l))
        self.f3 = (l2 for l2 in (l1 for l1 in self.f2 if self.content_like_func(l1)) if self.content_notlike_func(l2))
        #ifilter(self.content_notlike_func, ifilter(self.content_like_func, self.f2))
        self.f4 = islice(self.f3, 0, self.fltr['last'] and self.fltr['last'] or None)
        self.for_c = self.f4

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

    def run(self):
        semaphore.acquire()
        for l in self.for_c:
            if self.evt.isSet():
                break
           # if ( self.stopthread.isSet() ):
           #     self.stopthread.clear()
           #     break
                gtk.gdk.threads_enter()
            self.model.append((l['the_time'], l['computer'], l['logtype'], \
                l['evt_type'], l['source'], l['msg'], "#FFFFFF"))
            gtk.gdk.threads_leave()
        semaphore.release()
        lock.acquire()
        gtk.gdk.threads_enter()
        curr_frac = self.progress.get_fraction() + self.frac
        gtk.gdk.threads_leave()
        if curr_frac>=1.0-self.frac/2.:
            gtk.gdk.threads_enter()
            self.progress.set_fraction(1.0)
            self.progress.set_text("Complete")
            for sl in self.sens_list:
                sl.set_sensitive(True)
                gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self.progress.set_fraction(curr_frac)
            gtk.gdk.threads_leave()
        lock.release()

def datetime_intersect(t1start, t1end, t2start, t2end):
    return (t1start <= t2start and t2start <= t1end) or \
           (t2start <= t1start and t1start <= t2end)

def get_m_time(path):
    deq = deque()
    f = open(path, 'r')
    deq.extend(f.readlines())
    f.close()
    while deq:
        string = deq.pop()
        try:
            string = string.decode("cp1251")
        except UnicodeDecodeError:
            pass
        try:
            parsed_s = file_log.parseString(string)
            dt = parsed_s.get('datetime', None)
        except:
            pass
        else:
            if dt:
                return dt
    ed = time.localtime(os.path.getmtime(path))
    return datetime.datetime(ed.tm_year,
                    ed.tm_mon,
                    ed.tm_mday,
                    ed.tm_hour,
                    ed.tm_min,
                    ed.tm_sec)

def file_preparator(folders, fltr, queue):
    for key, value in folders.iteritems():
        for f in os.listdir(key):
            fullf = os.path.join(key,f)
            if os.path.isfile(fullf):
                try:
                    pf = filename.parseString(f)
                except ParseException:
                    continue
                if pf['logname']+pf['logname2'] in value:
                    f_end_date = get_m_time(fullf)
                    sd = time.localtime(os.path.getctime(fullf))
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


class FileLogWorker(threading.Thread):
    def __init__(self, model, q, stp):
        threading.Thread.__init__(self)
        self.model = model
        self.queue = q
        self.deq = deque()
        self.buf_deq = deque()
        self.stop = stp

    def load(self):
        f = open(self.path, 'r')
        self.deq.extend(f.readlines())
        f.close()
        at = [0,0]
        while self.deq:
            if self.stop.isSet():
                self.deq.clear()
                self.buf_deq.clear()
                break
            string = self.deq.pop()
            try:
                string = string.decode("cp1251")
            except UnicodeDecodeError:
                pass
            if error_flag.search(string.strip()):
                at[0]+=1
            if "Exception" in string:
                at[1]+=1
            parsed_s = file_log.searchString(string)
            if not parsed_s:
                self.buf_deq.appendleft(string)
            else:
                l_type = (at[0]>0 and at[1]>0) and "ERROR" or "?"
                at[0]=0
                at[1]=0
                self.buf_deq.appendleft(parsed_s[0][1])
                msg = "".join(self.buf_deq)
                self.buf_deq.clear()
                yield (parsed_s[0][0], "", "", l_type , self.path, msg, "#FFFFFF")

    def filter(self):
        def f_date(l):
            try:
                if l[0]<self.fltr['date'][0]:
                    raise StopIteration
            except TypeError:
                raise StopIteration
            return (l[0]<=self.fltr['date'][1] and \
                l[0]>=self.fltr['date'][0])

        for l in (l1 for l1 in self.load() if f_date(l1)):
            yield l

    def group(self):
        for k, g in groupby(self.filter(), lambda x: [x[0],x[1],x[2],x[3],x[4]]):
            yield (k[0], k[1], k[2], k[3], k[4],\
                "".join((m[5] for m in g)),
                "#FFFFFF")


    def run(self):
        while 1:
            self.path = self.queue.get()
            for l in self.group():
                gtk.gdk.threads_enter()
                self.model.append(l)
                gtk.gdk.threads_leave()


