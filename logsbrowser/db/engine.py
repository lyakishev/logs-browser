import sqlite3
import config
import functions
from datetime import datetime
from utils.profiler import time_it
from utils.ranges import ranges


_dbconn = sqlite3.connect(config.SQL_URI, check_same_thread = False)
_dbconn.create_function("regexp", 2, functions.regexp)
_dbconn.create_function("regex", 3, functions.regex)
_dbconn.create_function("pretty", 1, functions.pretty_xml)
_dbconn.create_function("group_logname", 1, functions.group_logname)
_dbconn.execute("PRAGMA synchronous=OFF;")

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
    print 'interrupt'
    _dbconn.interrupt()

def insert_many(table, iter_):
    _dbconn.executemany("insert into %s values (last_insert_rowid()+1,?,?,?,?,?,?,?);" %
                                    table, iter_)

def create_new_table(table, index=True):
    if index:
        sql = """create virtual table %s using fts4(lid INTEGER PRIMARY KEY,
                 date text, computer text,
                 logname text,
                 type text, source text, event integer, log text);""" % table
    else:
        sql = """create table %s (lid INTEGER PRIMARY KEY,
                 date text, computer text, logname text,
                 type text, source text, event integer, log text);""" % table
    _dbconn.execute(sql)


def drop(table):
    _dbconn.execute("drop table if exists %s;" % table)

def get_msg(rows, table):
    rows_clause = ranges(rows, 'lid')
    msg_sql = """select date, logname, type, source, pretty(log) 
                 from %s where %s order by date asc, %s
                 desc;""" % (table, rows_clause, 'lid')
    cur = _dbconn.cursor()
    cur.execute(msg_sql)
    result = cur.fetchall()
    dates = [datetime.strptime(r[0],"%Y-%m-%d %H:%M:%S.%f") for r in result]
    lognames = [r[1] for r in result]
    types = [r[2] for r in result]
    sources = [r[3] for r in result]
    msg = [r[4] for r in result]
    return (dates, lognames, types, sources, msg)

@time_it
def execute(sql):
    functions.group_logname.clear()
    cur = _dbconn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    desc = cur.description
    return (desc, rows)
