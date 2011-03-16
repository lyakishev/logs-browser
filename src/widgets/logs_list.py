# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from widgets.log_window import LogWindow
from widgets.query_constructor import Query
from log_window import SeveralLogsWindow
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
from colorsys import *
from operator import mul


BREAK_EXECUTE_SQL = False

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
    text = empty_lines.sub("",xml_new.sub(xml_pretty, text))
    return text.replace("&quot;", '"').replace("&gt;",">").replace("&lt;","<")



def strip(t):
    return t.strip()

def regexp(pattern, field):
    ret = re.compile(pattern).search(field)
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

class ColorAgg:
    def __init__(self):
        self.colors = []

    def circ_ave(self, a0, a1):
        r = (a0+a1)/2., ((a0+a1+360)/2.)%360 
        if min(abs(a1-r[0]), abs(a0-r[0])) < min(abs(a0-r[1]), abs(a1-r[1])):
            return r[0]
        else:
            return r[1]

    def step(self, value):
        if value != '#fff':
            c = gtk.gdk.color_parse(value)
            self.colors.append((c.red,c.green,c.blue))

    def finalize(self):
        if self.colors:
            new_colors = set([rgb_to_hsv(*c) for c in set(self.colors)])
            hue = reduce(self.circ_ave, [c[0]*360 for c in new_colors])/360.
            saturations = [c[1] for c in new_colors]
            sat = sum(saturations)/float(len(saturations))
            values = [c[2]/65535. for c in new_colors]
            value = sum(values)/float(len(values))
            mix_color=gtk.gdk.color_from_hsv(hue, sat, value)
            return mix_color.to_string()
        else:
            return '#fff'


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


DB_CONN = sqlite3.connect(":memory:", check_same_thread = False,
                  detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
DB_CONN.create_function("strip", 1, strip)
DB_CONN.create_function("regexp", 2, regexp)
DB_CONN.create_function("regex", 3, regex)
DB_CONN.create_function("pretty", 1, pretty_xml)
DB_CONN.create_aggregate("rows", 1, RowIDsList)
DB_CONN.create_aggregate("error", 1, AggError)
DB_CONN.create_aggregate("color_agg", 1, ColorAgg)

def callback():
    global BREAK_EXECUTE_SQL
    if BREAK_EXECUTE_SQL:
        BREAK_EXECUTE_SQL = False
        DB_CONN.interrupt()
    while gtk.events_pending():
        gtk.main_iteration()

DB_CONN.set_progress_handler(callback, 1000)

class LogList:
 
    def __init__(self):
        self.db_conn = DB_CONN
        self.hash_value = ""
        self.view = gtk.TreeView()
        self.view.connect('row-activated', self.show_log)
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.model = None
        self.columns = []
        self.cur = self.db_conn.cursor()
        self.cur.execute("PRAGMA synchronous=OFF;")
        self.headers = []
        self.fts = False


    def create_new_table(self, index=True):
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
        rows_sql = sql.replace("this", self.hash_value)
        try:
            self.cur.execute(rows_sql)
        except sqlite3.OperationalError, e:
            #print "Interrupted"
            print e
            self.view.set_model(self.model)
            self.view.thaw_child_notify()
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
        
    def show_log(self, view, *args):
        selection = view.get_selection()
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
    def __init__(self, ntb):
        super(LogListWindow, self).__init__()
        self.log_list = LogList()
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.logs_window.add(self.log_list.view)
        self.stop = False

        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        exec_btn = gtk.ToolButton(gtk.STOCK_EXECUTE)
        exec_btn.connect("clicked", self.execute)

        self.break_btn = gtk.ToolButton(gtk.STOCK_CANCEL)
        self.break_btn.connect("clicked", self.cancel)

        sep1 = gtk.SeparatorToolItem()

        query_btn = gtk.ToggleToolButton(gtk.STOCK_PAGE_SETUP)
        query_btn.connect("clicked", self.show_query)
        query_btn.set_is_important(True)
        query_btn.set_label("Edit Query")


        sep2 = gtk.SeparatorToolItem()

        lwin_btn = gtk.ToolButton(gtk.STOCK_FILE)
        lwin_btn.connect("clicked", self.show_log_window)
        lwin_btn.set_is_important(True)
        lwin_btn.set_label("Show Log")
        toolbar.insert(exec_btn, 0)
        toolbar.insert(self.break_btn, 1)
        toolbar.insert(sep1, 2)
        toolbar.insert(query_btn, 3)
        toolbar.insert(sep2, 4)
        toolbar.insert(lwin_btn, 5)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)


        self.filter_logs = Query(self.log_list)
        self.paned = gtk.VPaned()
        self.box = gtk.VBox()

        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.logs_window, True, True)

        self.sens_list = ([exec_btn, lwin_btn, self.logs_window]+
                            self.filter_logs.sens_list)

        self.add(self.box)
        self.show_all()
        self.break_btn.set_sensitive(False)

        self.sens_list = [exec_btn,lwin_btn]+self.filter_logs.sens_list
        self.ntb = ntb

    def execute(self, *args):
        self.break_btn.set_sensitive(True)
        self.ntb.set_sens(False)
        self.log_list.execute(self.filter_logs.get_sql())
        self.ntb.set_sens(True)
        self.break_btn.set_sensitive(False)

    def cancel(self, *args):
        global BREAK_EXECUTE_SQL
        BREAK_EXECUTE_SQL = True

    def show_query(self, button):
        if button.get_active():
            self.box.remove(self.logs_window)
            self.paned.pack1(self.logs_window, True, False)
            self.paned.pack2(self.filter_logs, False, False)
            self.paned.set_position(575)
            self.box.pack_end(self.paned)
        else:
            self.paned.remove(self.logs_window)
            self.paned.remove(self.filter_logs)
            self.box.remove(self.paned)
            self.box.pack_end(self.logs_window)
        self.show_all()

    def show_log_window(self, *args):
        view = self.log_list.view
        selection = view.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        if len(pathlist) > 1:
            SeveralLogsWindow(self.log_list,
                              self.log_list.model.get_iter(pathlist[0]),
                              selection)
        else:
            self.log_list.show_log(self.log_list.view)
            

    def text_grab_focus(self, *args):
        self.filter_logs.text.grab_focus()

    @property
    def get_view(self):
        return self.log_list.view
