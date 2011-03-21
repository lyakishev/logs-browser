import cProfile
import pstats
import datetime

def profile(function):
    def wrapper(*args):
        f = function
        cProfile.runctx('apply(f,args)',
                        globals(), locals(), "cproof")
        p = pstats.Stats("cproof")
        p.sort_stats('time').print_stats()
    return wrapper


def time_it(function):
    def wrapper(*args,**kw):
        dt = datetime.datetime.now()
        res = function(*args,**kw)
        print datetime.datetime.now() - dt
        return res
    return wrapper
