from db.engine import insert_many
from lparser.files.worker import filelogworker as fworker
import sys
if sys.platform == 'win32':
    from lparser.events.worker import evlogworker as eworker
from utils.profiler import time_it, profile
from multiprocessing import Pool, Event
from itertools import chain
from threading import Thread
import time

@time_it
def process(table, sources, dates, callback):

    def _process(worker, logs):
        for path, log in logs:
            stop_ = callback(log)
            if stop_:
                break
            insert_many(table, worker(dates, path, log))
        
    flogs, elogs = sources
    _process(fworker, flogs)
    if elogs:
        _process(eworker, elogs)

def _worker(args):
    return list(args[3](args[0],args[1],args[2]))

def _mix_sources(sources, dates):
    sources_for_worker = []
    for p, l in sources[0]:
        sources_for_worker.append((dates, p, l, fworker))
    for p, l in sources[1]:
        sources_for_worker.append((dates, p, l, eworker))
    return sources_for_worker

def callback_generator(iterable, callback):
    for item in iterable:
        if callback():
            raise StopIteration
        yield item
    
@time_it
def mp_process(table, sources, dates, callback):
    pool = Pool()
    sources_for_worker = _mix_sources(sources, dates)
    pool_result = pool.imap_unordered(_worker, sources_for_worker)
    work = callback_generator(pool_result, callback)
    insert_many(table, chain.from_iterable(work))
    pool.close()
