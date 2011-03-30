from db.engine import insert_many
from lparser.files.worker import filelogworker as fworker
from source.worker import file_preparator
import sys
if sys.platform == 'win32':
    from lparser.events.worker import evlogworker as eworker


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
 
    
