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

import sqlite3
import config
import functions
from datetime import datetime
from utils.profiler import time_it
from utils.ranges import ranges
import time


_dbconn = sqlite3.connect(config.SQL_URI)

_dbconn.execute("PRAGMA synchronous = OFF;")
_dbconn.execute("PRAGMA journal_mode = OFF;")
_dbconn.execute("PRAGMA PAGE_SIZE = 4096;")

_dbconn.create_function("regexp", 2, functions.regexp)
_dbconn.create_function("match", 2, functions.rmatch)
_dbconn.create_function("regex", 3, functions.regex)
_dbconn.create_function("pretty", 1, functions.pretty)
_dbconn.create_function("group_logname", 1, functions.group_logname)
_dbconn.create_function("iregexp", 2, functions.iregexp)
_dbconn.create_function("not_iregexp", 2, functions.not_iregexp)
_dbconn.create_function("icontains", 2, functions.icontains)
_dbconn.create_function("not_icontains", 2, functions.not_icontains)
_dbconn.create_function("contains", 2, functions.contains)
_dbconn.create_function("not_contains", 2, functions.not_contains)
_dbconn.create_function("rmatch", 2, functions.rmatch)
_dbconn.create_function("intersct", 2, functions.intersct)


def register_agg(name, nargs, object_):
    _dbconn.create_aggregate(name, nargs, object_)
    functions.aggregate_functions.append(name)

register_agg("error", 1, functions.AggError)
register_agg("rows", 1, functions.RowIDsList)
register_agg("color_agg", 1, functions.ColorAgg)
    

DBException = sqlite3.OperationalError

def close_conn():
    _dbconn.close()

def set_callback(callback):
    _dbconn.set_progress_handler(callback, 10000)

def interrupt():
    _dbconn.interrupt()

@time_it
def insert_many(table, iter_):
    _dbconn.executemany("insert into %s values (last_insert_rowid()+1,?,?,?,?,?,?,?);" %
                                    table, iter_)
    _dbconn.commit()

def create_new_table(table, index=True):
    if index:
        sql = """create virtual table %s using fts4(lid INTEGER PRIMARY KEY,
                 date text, computer text,
                 logname text,
                 type text, source text, event integer, log text);""" % table
        _dbconn.execute(sql)
    else:
        sql = """create table %s (lid INTEGER PRIMARY KEY,
                 date text, computer text, logname text,
                 type text, source text, event integer, log text);""" % table
        _dbconn.execute(sql)
        sql_index = """create index %s_index on %s (logname, computer);""" % (table, table)
        _dbconn.execute(sql_index)


def drop(table):
    _dbconn.execute("drop table if exists %s;" % table)
    _dbconn.execute("drop index if exists %s_index;" % table)

@time_it
def get_msg(rows, table):
    sql = """select date, logname, type, source, log
                 from %s where lid in (%s) order by date asc, lid desc;""" % (table, rows)
    cur = _dbconn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    dates = [r[0] for r in result]
    lognames = (r[1] for r in result)
    types = (r[2] for r in result)
    sources = (r[3] for r in result)
    msg = (r[4] for r in result)
    return (dates, lognames, types, sources, msg)

@time_it
def execute(sql):
    functions.group_logname.clear()
    cur = _dbconn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    desc = cur.description
    return (desc, rows)
