# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from widgets.log_window import LogWindow
from widgets.color_parser import ColorParser, SQLExecuter
import re
import pickle
import hashlib
import sqlite3
from datetime import datetime
import pango
from operator import itemgetter
import os



def callback():
    while gtk.events_pending():
        gtk.main_iteration()

def comp(t):
    return [p for p in t.split(os.sep) if p][0]

def strip(t):
    return t.strip()

def regexp(t, pattern):
    try:
        ret = re.compile(pattern).search(t)
    except:
        return False
    else:
        return True if ret else False

def regex(t, pattern, gr):
    try:
        ret = re.compile(pattern).search(t).group(gr)
    except:
        pass
    else:
        return ret

def utf_decode(t):
    try:
        txt = t.decode('utf-8').encode('utf-8')
    except UnicodeDecodeError:
        txt = t.decode('cp1251').encode('utf-8')
    return txt

class AggError:
    def __init__(self):
        self.type_ = '?'

    def step(self, value):
        if value == 'ERROR':
            self.type_ = 'ERROR'

    def finalize(self):
        return self.type_

class RowIDsList:
    def __init__(self):
        self.rowids = []

    def step(self, value):
        self.rowids.append(value)

    def finalize(self):
        return str(self.rowids)[1:-1]

SQL_RE = re.compile("".join(["(?i)select(?:distinct|all)?",
        "(.+?)",
        "\s+(?:from|where|group|order|union|intersect|except|limit)"]))

def add_rows_to_select(sql):
    new_sql = []
    start = 0
    for m in SQL_RE.finditer(sql):
        begin = sql[start:m.start(1)]
        new_sql.append("".join([begin,m.group(1),", rows(rowid) as rows_for_log_window"]))
        start = m.end(1)
    new_sql.append(sql[start:])
    return "".join(new_sql)

class LogList:
    db_conn = sqlite3.connect(":memory:", check_same_thread = False,
                      detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    db_conn.create_function("strip", 1, strip)
    db_conn.create_function("regexp", 2, regexp)
    db_conn.create_function("regex", 3, regex)
    db_conn.create_function("comp", 1, comp)
    db_conn.create_aggregate("error", 1, AggError)
    db_conn.create_aggregate("rows", 1, RowIDsList)
    #TODO# db_conn.create_function("pretty_xml", 1, pretty_xml)
    db_conn.text_factory = utf_decode
    db_conn.set_progress_handler(callback, 1000)

    def __init__(self):
        self.hash_value = ""
        self.view = gtk.TreeView()
        self.view.connect('row-activated', self.show_log)
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.model = None
        self.columns = []
        self.cur = self.db_conn.cursor()
        self.cur.execute("PRAGMA synchronous=OFF;")
        self.sql = ""
        self.headers = []


    def create_new_table(self, index=False):
        if index:
            sql = """create virtual table %s using fts4(date text, computer text,
                     log_name text,
                     type text, source text, log text);""" % self.hash_value
        else:
            sql = """create table %s (date text, computer text, log_name text,
                     type text, source text, log text);""" % self.hash_value
        self.cur.execute(sql)
        self.db_conn.commit()

    def insert(self, log):
        self.cur.execute("insert into %s values (?,?,?,?,?,?);" % self.hash_value,
                         log)

    def insert_many(self, iter_):
        self.cur.executemany("insert into %s values (?,?,?,?,?,?);" % \
                                        self.hash_value, iter_)

    def execute(self, sql):
        self.cur.close()
        self.cur = self.db_conn.cursor()
        now = datetime.now
        self.view.freeze_child_notify()
        self.view.set_model(None)
        self.sql = sql.replace("this", self.hash_value)
        rows_sql = self.sql#add_rows_to_select(self.sql)
        dt = now()
        self.cur.execute(rows_sql)
        print "Select *:", now() - dt
        rows = self.cur.fetchall()
        if rows:
            self.headers = map(itemgetter(0),self.cur.description)
            headers = self.headers
            self.set_new_list_store(headers)
            self.build_view(headers)
            dt = now()
            for row in rows:
                self.model.append(row)
            print "Filling Liststore: ", now() - dt
            #if 'date' in headers:
            #    self.model.set_sort_column_id(headers.index('date'), gtk.SORT_DESCENDING)
            self.view.set_model(self.model)
        self.view.thaw_child_notify()

    def set_new_list_store(self, cols):
        args = [gobject.TYPE_STRING for i in cols]
        self.model = gtk.ListStore(*args)

    def build_view(self, args):
        for col in self.columns:
            self.view.remove_column(col)
        self.columns = []
        for number, header in enumerate(args):
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', False)
            renderer.props.wrap_width = 640
            renderer.props.wrap_mode = pango.WRAP_WORD
            if 'bgcolor' in args:
                col = gtk.TreeViewColumn(header, renderer,
                                    text=number,
                                    cell_background=args.index('bgcolor'))
            else:
                col = gtk.TreeViewColumn(header, renderer,
                                    text=number)
            self.columns.append(col)
            col.set_sort_column_id(number)
            col.set_resizable(True)
            self.view.append_column(col)
            if header in ('rows_for_log_window', 'bgcolor'):
                col.set_visible(False)

    def set_hash(self, params):
        pick = pickle.dumps(params)
        hash_v = hashlib.md5(pick).hexdigest()
        self.hash_value = "".join(["_",hash_v])

    def clear(self):
        if self.model:
            self.model.clear()
        if self.hash_value:
            self.cur.execute("drop table %s;" % self.hash_value)
            self.db_conn.commit()
            self.cur.close()
            self.cur = self.db_conn.cursor()
        
    def show_log(self, path, column, params):
        selection = path.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        (model, iter_) = selection.get_selected()
        LogWindow(self, iter_, selection)
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        return

    def get_msg_by_rowids(self, iter_):
        rows = self.model.get_value(iter_,
                               self.headers.index('rows_for_log_window'))
        msg_sql = "select group_concat(log) from %s where rowid in (%s) order by date asc;" % \
                                            (self.hash_value, rows)
        self.cur.execute(msg_sql)
        result = self.cur.fetchall()
        return result[0][0]


class LogListWindow(gtk.Frame):
    def __init__(self):
        super(LogListWindow, self).__init__()
        self.log_list = LogList()
        logs_window = gtk.ScrolledWindow()
        logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        logs_window.add(self.log_list.view)
        exp = gtk.Expander("Filter")
        exp.connect("activate", self.text_grab_focus)
        self.filter_logs = SQLExecuter(self.log_list.model, self.log_list.view,
                            self.log_list)
        exp.add(self.filter_logs)
        box = gtk.VBox()
        self.add(box)
        box.pack_start(logs_window, True, True)
        box.pack_start(exp, False, False, 2)
        self.show_all()

    def text_grab_focus(self, *args):
        self.filter_logs.text.grab_focus()

    @property
    def get_view(self):
        return self.log_list.view
