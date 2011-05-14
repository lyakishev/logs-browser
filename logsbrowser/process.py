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

_e_stop = Event()

def _worker(args):
    if _e_stop.is_set():
        raise StopIteration
    return list(args[3](args[0],args[1],args[2]))

def _mix_sources(sources, dates):
    sources_for_worker = []
    for p, l in sources[0]:
        sources_for_worker.append((dates, p, l, fworker))
    for p, l in sources[1]:
        sources_for_worker.append((dates, p, l, eworker))
    return sources_for_worker
    

def _mp_process(table, sources, dates):
    pool = Pool()
    sources_for_worker = _mix_sources(sources, dates)
    work = chain.from_iterable(pool.imap(_worker, sources_for_worker))
    insert_many(table, work)
    pool.close()


@time_it
def mp_process(table, sources, dates, callback):
    t=Thread(target=_mp_process, args=(table, sources, dates))
    t.start()
    while t.is_alive():
        callback(_e_stop)
        time.sleep(0.2)
    _e_stop.clear()
    

