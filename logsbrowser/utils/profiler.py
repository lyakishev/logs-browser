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
        print function.__name__, datetime.datetime.now() - dt
        return res
    return wrapper

def trace(f):
    def wrapper(*args, **kwargs):
        print f.func_name, args, kwargs
        r = f(*args, **kwargs)
        return r
    return wrapper
    


