# LogsBrowser is program for find and analyze logs.
# Copyright (C) <2010-2011>  <Lyakishev Andrey (lyakav@gmail.com)>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from db.engine import insert_many
from lparser.files.worker import filelogworker as fworker
import sys
if sys.platform == 'win32':
    from lparser.events.worker import evlogworker as eworker
# from utils.profiler import time_it, profile
from multiprocessing import Event, Process, Queue, JoinableQueue, Value, cpu_count
from itertools import chain
from threading import Thread
import time
from Queue import Empty as qEmpty

PROCESSES = cpu_count()

# @time_it


def process(table, sources, dates, callback):

    def _process(worker, logs):
        for path, log, funcs in logs:
            stop_ = callback(log)
            if stop_:
                break
            insert_many(table, (val[0]
                        for val in worker(dates, path, log, funcs)))
    flogs, elogs = sources
    _process(fworker, flogs)
    if elogs:
        _process(eworker, elogs)


class Processor(Process):
    def __init__(self, in_queue, out_queue, event, val):
        super(Processor, self).__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.event = event
        self.value = val

    def run(self):
        stop = self.event.is_set
        put = self.out_queue.put
        get = self.in_queue.get_nowait
        while 1:
            try:
                worker, dates, path, log, parser = get()
            except qEmpty:
                break
            else:
                buffer_, chars = [], 0
                for row, ch in worker(dates, path, log, parser):
                    chars += ch
                    buffer_.append(row)
                    if chars >= 16*1024:
                        put(buffer_)
                        buffer_, chars = [], 0
                put(buffer_)
                self.in_queue.task_done()
                self.value.value += 1
        self.in_queue.join()
        put(None)


def _mix_sources(sources, dates):
    sources_for_worker = JoinableQueue()
    for p, l, funcs in sources[0]:
        sources_for_worker.put((fworker, dates, p, l, funcs))
    for p, l, funcs in sources[1]:
        sources_for_worker.put((eworker, dates, p, l, funcs))
    return sources_for_worker


def terminate(processes):
    for process in processes:
        process.terminate()


def generator_from_queue(queue, e_stop, vall, callback, p):
    get = queue.get
    stop = e_stop.is_set
    c = 0
    while 1:
        callback(e_stop, vall.value)
        if stop():
            terminate(p)
            queue.close()
            raise StopIteration
        if c == PROCESSES:
            break
        val = get()
        if val == None:
            c += 1
            continue
        yield val


def _mp_process(table, sources, dates, stop, val, callback):
    sources_for_worker = _mix_sources(sources, dates)
    insert_queue = Queue()
    processes = []
    for i in xrange(PROCESSES):
        p = Processor(sources_for_worker, insert_queue, stop, val)
        processes.append(p)
        p.daemon = True
        p.start()
    insert_many(table, chain.from_iterable(generator_from_queue(insert_queue,
                                                                stop, val, callback, processes)))
    sources_for_worker.close()
    insert_queue.close()

# @time_it


def mp_process(table, sources, dates, callback):
    _e_stop = Event()
    val = Value('i', 0)
    _mp_process(table, sources, dates, _e_stop, val, callback)
    _e_stop.clear()
