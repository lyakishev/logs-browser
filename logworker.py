from evs import *
import threading
import pygtk
pygtk.require("2.0")
import gtk, gobject
from parse import filename
from pyparsing import ParseException
import os
import time
import datetime
from itertools import ifilter, islice

max_connections = 5
semaphore = threading.BoundedSemaphore(value=max_connections)


class LogWorker(threading.Thread):

    #stopthread = threading.Event()

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
        self.f1 = self.date_generator(self.date_func, getEventLogs(self.comp, self.log))
        self.f2 = ifilter(self.type_func, self.f1)
        self.f3 = ifilter(self.content_notlike_func, ifilter(self.content_like_func, self.f2))
        self.f4 = islice(self.f3, 0, self.fltr['last'] and self.fltr['last'] or None)
        self.for_c = self.f4

    def f_date(self, l):
        if l['the_time']<=self.fltr['date'][1] and l['the_time']>=self.fltr['date'][0]:
            return l

    def date_generator(self, func, gen):
        for l in gen:
            if l['the_time']<self.fltr['date'][0]:
                break
            else:
                yield func(l)

    def f_likecont(self, l):
        if eval(self.fltr['content'][0]):# in l['msg']:
            return True

    def f_notlikecont(self, l):
        if self.fltr['content'][1] not in l['msg']:
            return True

    def f_type(self, l):
        if l['evt_type'] in self.fltr['types']:
            return True

    def run(self):
        semaphore.acquire()
        for l in self.for_c:
            if self.evt.isSet():
                break
           # if ( self.stopthread.isSet() ):
           #     self.stopthread.clear()
           #     break
            if l:
                gtk.gdk.threads_enter()
                self.model.append((l['the_time'], l['computer'], l['logtype'], \
                    l['evt_type'], l['source'], l['msg'], "#FFFFFF"))
                gtk.gdk.threads_leave()
        semaphore.release()
        gtk.gdk.threads_enter()
        curr_frac = self.progress.get_fraction() + self.frac
        gtk.gdk.threads_leave()
        if curr_frac>=1.0:
            gtk.gdk.threads_enter()
            self.progress.set_fraction(1.0)
            self.progress.set_text("Complete")
            gtk.gdk.threads_leave()
            for sl in self.sens_list:
                gtk.gdk.threads_enter()
                sl.set_sensitive(True)
                gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self.progress.set_fraction(curr_frac)
            gtk.gdk.threads_leave()

def datetime_intersect(t1start, t1end, t2start, t2end):
    return (t1start <= t2start and t2start <= t1end) or \
           (t2start <= t1start and t1start <= t2end)


class FileLogWorker():
    def __init__(self, files, fltr):
        self.files = files
        self.fltr = fltr

    def get_files(self):
        for key, value in self.files.iteritems():
            for f in os.listdir(key):
                fullf = os.path.join(key,f)
                if os.path.isfile(fullf):
                    try:
                        pf = filename.parseString(f)
                    except ParseException:
                        continue
                    if pf['logname']+pf['logname2'] in value:
                        ed = time.localtime(os.path.getmtime(fullf))
                        f_end_date = datetime.datetime(ed.tm_year,
                            ed.tm_mon,
                            ed.tm_mday,
                            ed.tm_hour,
                            ed.tm_min,
                            ed.tm_sec)
                        sd = time.localtime(os.path.getctime(fullf))
                        f_start_date = datetime.datetime(sd.tm_year,
                            sd.tm_mon,
                            sd.tm_mday,
                            sd.tm_hour,
                            sd.tm_min,
                            sd.tm_sec)
                        if datetime_intersect(self.fltr['date'][0],
                                                self.fltr['date'][1],
                                                f_start_date, f_end_date):
                            self.process(fullf)

    def process(self, path):
        f = open(path, 'r')
        s='\n'.join(f.readlines[:3])
        print s
        f.close()
