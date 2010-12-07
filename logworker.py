from evs import *
import threading
import pygtk
pygtk.require("2.0")
import gtk, gobject

semaphore = threading.BoundedSemaphore(value=5)


class LogWorker(threading.Thread):

    #stopthread = threading.Event()

    def __init__(self, comp, log, fltr, model, progress, frac):
        threading.Thread.__init__(self)
        self.ret_self = lambda l: l
        self.comp = comp
        self.log = log
        self.fltr = fltr
        self.model = model
        self.progress = progress
        self.frac = frac
        self.type_func = self.fltr['types'] and self.f_type or self.ret_self
        self.date_func = fltr['date'] and self.f_date or self.ret_self
        self.content_like_func = fltr['content'][0] and self.f_likecont or self.ret_self
        self.content_notlike_func = fltr['content'][1] and self.f_notlikecont or self.ret_self
        #self.last_func = fltr['last'] and self.f_last or (lambda l, c: l)
        self.f1 = (self.date_generator(self.date_func, getEventLogs(self.comp, self.log)))
        self.f2 = (self.type_func(l) for l in self.f1)
        self.f3 = (self.content_notlike_func(l) for l in (self.content_like_func(l1) for l1 in self.f2))
        #self.f4 = (self.last_func(l, i) for i,l inself.f3)
        self.f4 = self.last_gen(self.f3)
        self.for_c = self.f4

    def last_gen(self, gen):
        if self.fltr['last'] != 0:
            counter = 0
            for l in gen:
                if l:
                    if counter < self.fltr['last']:
                        counter+=1
                        yield l
                    else:
                        return
        else:
            for l in gen:
                if l:
                    yield l
    def f_date(self, l):
        if l:
            if l['the_time']<=self.fltr['date'][1] and l['the_time']>=self.fltr['date'][0]:
                return l

    def date_generator(self, func, gen):
        try:
            for l in gen:
                if l['the_time']<self.fltr['date'][0]:
                    return
                else:
                    yield func(l)
        except IndexError:
            for l in gen:
                yield func(l)

    def f_likecont(self, l):
        if l:
            if self.fltr['content'][0] in l['msg']:
                return l

    def f_notlikecont(self, l):
        if l:
            if self.fltr['content'][1] not in l['msg']:
                return l

    def f_type(self, l):
        if l:
            if l['evt_type'] in self.fltr['types']:
                return l

    def run(self):
        semaphore.acquire()
        print "%s %s acquire" % (self.log, self.comp)
        for l in self.for_c:
           # if ( self.stopthread.isSet() ):
           #     self.stopthread.clear()
           #     break
            if l:
                gtk.gdk.threads_enter()
                self.model.append((l['the_time'], l['computer'], l['logtype'], l['evt_type'], l['source'], l['msg']))
                #myGUI.run()
                gtk.gdk.threads_leave()
        print "%s %s release" % (self.log, self.comp)
        semaphore.release()
        gtk.gdk.threads_enter()
        curr_frac = self.progress.get_fraction() + self.frac
        self.progress.set_fraction((curr_frac>1.0) and 1.0 or curr_frac)
        gtk.gdk.threads_leave()
                #print l['the_time'], l['computer'], l['logtype'], l['evt_type'], l['source'], l['msg']
