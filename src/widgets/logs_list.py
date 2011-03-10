# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from widgets.log_window import LogWindow
from widgets.query_constructor import Query
import re
import pickle
import hashlib
import sqlite3
from datetime import datetime
import pango
from operator import itemgetter
import os
import xml.dom.minidom
import profiler


xml_new = re.compile(r"(<\?xml.+?><(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
xml_bad = re.compile(r"((?<!>)<(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
empty_lines = re.compile("^$")

def xml_pretty(m):
        txt = m.group()
        try:
            xparse = xml.dom.minidom.parseString
            pretty_xml = xparse(txt.encode("utf-16")).toprettyxml()
        except xml.parsers.expat.ExpatError:
            #print traceback.format_exc()
            pretty_xml = txt.replace("><", ">\n<")
        return "\n" + pretty_xml

def xml_bad_pretty(m):
    txt = xml_pretty(m)
    new_txt = txt.splitlines()[2:]
    return "\n".join(new_txt)

def pretty_xml(t):
    text = xml_bad.sub(xml_bad_pretty, t)
    return empty_lines.sub("",xml_new.sub(xml_pretty, text))


def callback():
    while gtk.events_pending():
        gtk.main_iteration()

def strip(t):
    return t.strip()

def regexp(t, pattern):
    ret = re.compile(pattern).search(t)
    return True if ret else False

def regex(t, pattern, gr):
    try:
        ret = re.compile(pattern).search(t).group(gr)
    except:
        pass
    else:
        return ret

class RowIDsList:
    def __init__(self):
        self.rowids = []

    def step(self, value):
        self.rowids.append(value)

    def finalize(self):
        return str(self.rowids)[1:-1]

class AggError:
    def __init__(self):
        self.type_ = '?'

    def step(self, value):
        if value == 'ERROR':
            self.type_ = 'ERROR'

    def finalize(self):
        return self.type_

#SQL_RE = re.compile("".join(["(?i)select(?:distinct|all)?",
#        "(.+?)",
#        "\s+(?:from|where|group|order|union|intersect|except|limit)"]))
#
#def add_rows_to_select(sql):
#    new_sql = []
#    start = 0
#    for m in SQL_RE.finditer(sql):
#        begin = sql[start:m.start(1)]
#        new_sql.append("".join([begin,m.group(1),", rows(rowid) as rows_for_log_window"]))
#        start = m.end(1)
#    new_sql.append(sql[start:])
#    return "".join(new_sql)

class LogList:
    db_conn = sqlite3.connect(":memory:", check_same_thread = False,
                      detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    db_conn.create_function("strip", 1, strip)
    db_conn.create_function("regexp", 2, regexp)
    db_conn.create_function("regex", 3, regex)
    db_conn.create_function("pretty", 1, pretty_xml)
    db_conn.create_aggregate("rows", 1, RowIDsList)
    db_conn.create_aggregate("error", 1, AggError)
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
        self.fts = False


    def create_new_table(self, index=False):
        if index:
            self.fts = True
            sql = """create virtual table %s using fts4(date text, computer text,
                     log_name text,
                     type text, source text, log text);""" % self.hash_value
        else:
            self.fts = False
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
        self.view.freeze_child_notify()
        self.view.set_model(None)
        self.sql = sql.replace("this", self.hash_value)
        rows_sql = self.sql#add_rows_to_select(self.sql)
        self.cur.execute(rows_sql)
        rows = self.cur.fetchall()
        if rows:
            self.headers = map(itemgetter(0),self.cur.description)
            headers = self.headers
            self.set_new_list_store(headers)
            self.build_view(headers)
            for row in rows:
                self.model.append(row)
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
        rowids = rows.split(",")
        if len(rowids) < 1000:
            rows_clause = " or ".join(["rowid=%s" % s for s in rows.split(",")])
        else:
            rows_clause = "rowid in (%s)" % rows
        msg_sql = """select date, log_name, type, source, pretty(log) 
                    from %s where %s order by date asc, rowid
                            asc;""" % \
                                            (self.hash_value,
                                            rows_clause)
        self.cur.execute(msg_sql)
        result = self.cur.fetchall()
        msg = [r[4] for r in result]
        dates = []
        for r in result:
            try:
                dates.append(datetime.strptime(r[0],"%Y-%m-%d %H:%M:%S.%f"))
            except ValueError:
                dates.append(datetime.strptime(r[0],"%Y-%m-%d %H:%M:%S"))
        log_names = [r[1] for r in result]
        types = [r[2] for r in result]
        sources = [r[3] for r in result]
        return (dates, log_names, types, sources, msg)


class LogListWindow(gtk.Frame):
    def __init__(self):
        super(LogListWindow, self).__init__()
        self.log_list = LogList()
        logs_window = gtk.ScrolledWindow()
        logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        logs_window.add(self.log_list.view)
        exp = gtk.Expander("Filter")
        exp.connect("activate", self.text_grab_focus)
        self.filter_logs = Query()
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
