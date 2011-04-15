import sqlite3
import config
from functions import *
from datetime import datetime
from utils.profiler import time_it
from utils.ranges import ranges

_dbconn = sqlite3.connect(config.SQL_URI, check_same_thread = False)
_dbconn.create_function("strip", 1, strip)
_dbconn.create_function("regexp", 2, regexp)
_dbconn.create_function("regex", 3, regex)
_dbconn.create_function("pretty", 1, pretty_xml)
_dbconn.create_aggregate("error", 1, AggError)
_dbconn.create_aggregate("rows", 1, RowIDsList)
_dbconn.create_aggregate("color_agg", 1, ColorAgg)
_dbconn.execute("PRAGMA synchronous=OFF;")

DBException = sqlite3.OperationalError

def close_conn():
    _dbconn.close()

def set_callback(callback):
    _dbconn.set_progress_handler(callback, 1000)

def interrupt():
    _dbconn.interrupt()

def insert_many(table, iter_):
    _dbconn.executemany("insert into %s values (?,?,?,?,?,?,?,?);" %
                                    table, iter_)

def create_new_table(table, index=True):
    if index:
        sql = """create virtual table %s using fts4(lid INTEGER PRIMARY KEY
                 AUTOINCREMENT, date text, computer text,
                 log_name text,
                 type text, source text, event integer, log text);""" % table
    else:
        sql = """create table %s (lid INTEGER PRIMARY KEY
                 AUTOINCREMENT, date text, computer text, log_name text,
                 type text, source text, event integer, log text);""" % table
    _dbconn.execute(sql)


def drop(table):
    _dbconn.execute("drop table if exists %s;" % table)

def get_msg(rows, table):
    rows_clause = ranges(rows, 'lid')
    msg_sql = """select date, log_name, type, source, pretty(log) 
                 from %s where %s order by date asc, %s
                 desc;""" % (table, rows_clause, 'lid')
    cur = _dbconn.cursor()
    try:
        cur.execute(msg_sql)
    except DBException, e:
        print e
        rows_clause = "lid in (%s)" % rows
        msg_sql = """select date, log_name, type, source, pretty(log) 
                     from %s where %s order by date asc, %s
                     desc;""" % (table, rows_clause, 'lid')
        cur.execute(msg_sql)
    result = cur.fetchall()
    dates = [datetime.strptime(r[0],"%Y-%m-%d %H:%M:%S.%f") for r in result]
    log_names = [r[1] for r in result]
    types = [r[2] for r in result]
    sources = [r[3] for r in result]
    msg = [r[4] for r in result]
    return (dates, log_names, types, sources, msg)

def execute(sql):
    cur = _dbconn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    desc = cur.description
    return (desc, rows)
