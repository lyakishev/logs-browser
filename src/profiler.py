import cProfile
import pstats


def profile(function):
    def wrapper(*args):
        f = function
        cProfile.runctx('apply(f,args)',
                        globals(), locals(), "cproof")
        p = pstats.Stats("cproof")
        p.sort_stats('time').print_stats()
    return wrapper
