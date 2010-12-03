
class LogWorker(threading.Thread):

    stopthread = threading.Event()
    ret_self = lambda x: x

    def __init__(self, comp, log, fltr, date_params=None, content='')
        threading.Thread.__init__(self)
        self.comp = comp
        self.log = log
        self.date_params = date_params
        self.content = content
        self.date_func = fltr['date'] and self.f_date or ret_self
        self.content_func = fltr['content'] and self.f_cont or ret_self
        self.for_c=(self.content_func(l) for l in (self.date_generator(self.date_func, getEventLogs(self.comp, self.log))

    def f_date(self, l):
        if l['the_time']<=self.date_params['end_date'] and l['the_time']>=self.date_params['start_date']:
            return l

    def date_generator(self, func, gen):
        for l in gen:
            if l['the_time']<self.date_params['start_date']:
                return
            else:
                yield func(l)

    def f_cont(self, l):
        if self.content in l['msg']:
            return l

    def run(self):
        for l in self.for_c:
            if ( self.stopthread.isSet() ):
                self.stopthread.clear()
                break
            self.model.append((l['the_time'], l['computer'], l['logtype'], l['evt_type'], l['source'], l['msg']))
