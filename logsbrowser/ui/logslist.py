# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from logwindow import LogWindow
from query import Plain, QueryLoader
from logwindow import SeveralLogsWindow
from datetime import datetime
import pango
import os
from operator import mul, itemgetter, setitem
import db.engine as db
from db.parse import process
from utils.hash import hash_value, sql_to_hash
from utils.xmlqueries import QueriesManager
from dialogs import merror
import glib
from itertools import cycle
import config
from cellrenderercolors import CellRendererColors
from string import Template
from utils.profiler import time_it, profile
import pdb

def callback():
    while gtk.events_pending():
        gtk.main_iteration()

db.set_callback(callback)


class LogList(object):
    
    sql_context = {}
    _cache = {}

    def __init__(self):
        self.view = gtk.TreeView()
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.model = None
        self.columns = []
        self.headers = []
        self.fts = True
        self.name = ""
        self.table = ""
        self.cached_queries = []

    def change_name(self, name):
        try:
            self.sql_context.pop(self.name)
        except KeyError:
            pass
        finally:
            self.name = name
            self.sql_context[self.name] = self.table

    def execute(self, sql_templ, auto_lid):
        try:
            sql = process(sql_templ,self.get_context(), auto_lid)
        except Exception, e:
            merror(str(e))
            return
        print sql
        self.view.freeze_child_notify()
        self.view.set_model(None)
        sql_hash = sql_to_hash(sql)
        model = self._cache.get(sql_hash)
        if model:
            self.model = model[0]
            self.headers = model[1]
            self.build_view(self.headers)
            self.view.set_model(self.model)
            self.view.thaw_child_notify()
            return
        else:
            try:
                desc, rows = db.execute(sql)
            except db.DBException, e:
                merror(str(e))
                rows = None
            if rows:
                self.headers = map(itemgetter(0), desc)
                cols = [gobject.TYPE_STRING for i in self.headers]
                self.model = gtk.ListStore(*cols)
                self.build_view(self.headers)
                for row in iter(rows):
                    self.model.append(row)
                if 'bgcolor' in self.headers:
                    bgcolor = self.headers.index('bgcolor')
                    print bgcolor
                    white = set(["#fff", "None"])
                    colorcols = [n for n, c in enumerate(self.headers)
                                             if c.startswith('bgcolor')]
                    print colorcols
                    for row in self.model:
                        colors = set()
                        for cols in [r for r in [row[c] for c in colorcols] if r]:
                            for col1 in cols.split():
                                colors.add(col1)
                        wowhite = colors - white
                        if wowhite:
                            if len(wowhite)>1:
                                self.model.set_value(row.iter, bgcolor, " ".join(wowhite))
                            else:
                                self.model.set_value(row.iter, bgcolor, wowhite.pop())
                        else:
                            self.model.set_value(row.iter, bgcolor, "#fff")
                            
                self._cache[sql_hash] = (self.model, self.headers)
                self.cached_queries.append(sql_hash)
                self.view.set_model(self.model)
            self.view.thaw_child_notify()

    def build_view(self, args):
        for col in self.columns:
            self.view.remove_column(col)
        self.columns = []
        for number, header in enumerate(args):
            if 'bgcolor' in args:
                renderer = CellRendererColors()
                col = gtk.TreeViewColumn(header, renderer,
                                    text=number,
                                    backgrounds=args.index('bgcolor'))
            else:
                renderer = gtk.CellRendererText()
                col = gtk.TreeViewColumn(header, renderer,
                                    text=number)
            renderer.set_property('editable', False)
            renderer.props.wrap_width = 640
            renderer.props.wrap_mode = pango.WRAP_WORD
            self.columns.append(col)
            col.set_sort_column_id(number)
            col.set_resizable(True)
            self.view.append_column(col)
            if header == 'rows_for_log_window':
                self.rflw = number
                col.set_visible(False)
            if header.startswith('bgcolor'):
                col.set_visible(False)

    def clear(self):
        try:
            self.sql_context.pop(self.name)
        except KeyError:
            pass
        if self.model:
            self.model.clear()
        if self.table:
            db.drop(self.table)

    def clear_cached_queries(self):
        for q in self.cached_queries:
            self._cache.pop(q)

    def get_context(self):
        con = self.sql_context.copy()
        con.update({"this": self.table})
        return con
        
    def new_logs(self, index):
        self.clear()
        self.table = hash_value(datetime.now())
        self.sql_context[self.name] = self.table
        db.create_new_table(self.table, index)
        self.fts = index


class QMan:
    pass


class LogsListWindow(gtk.Frame):
    def __init__(self, ntb):
        super(LogsListWindow, self).__init__()
        self.log_list = LogList()
        self.log_list.view.connect('row-activated', self.show_log_window)
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.logs_window.add(self.log_list.view)

        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        exec_btn = gtk.ToolButton(gtk.STOCK_EXECUTE)
        exec_btn.connect("clicked", self.fill)

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

        sep3 = gtk.SeparatorToolItem()
        grid_btn = gtk.ToggleToolButton(gtk.STOCK_UNDERLINE)
        grid_btn.connect("clicked", self.show_gridlines)
        grid_btn.set_is_important(True)
        grid_btn.set_label("Grid Lines")
        
        toolbar.insert(exec_btn, 0)
        toolbar.insert(self.break_btn, 1)
        toolbar.insert(sep1, 2)
        toolbar.insert(query_btn, 3)
        toolbar.insert(sep2, 4)
        toolbar.insert(lwin_btn, 5)
        toolbar.insert(sep3, 6)
        toolbar.insert(grid_btn, 7)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)


        self.qm = QueriesManager(config.QUERIES_FILE)
        self.filter_logs = Plain()
        self.loader = QueryLoader(self.filter_logs, self.qm)
        self.paned = gtk.VPaned()
        self.box = gtk.VBox()

        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.logs_window, True, True)

        self.add(self.box)
        self.show_all()
        self.break_btn.set_sensitive(False)

        self.sens_list = [exec_btn,lwin_btn]+self.filter_logs.sens_list
        self.ntb = ntb

        if config.GRID_LINES:
            grid_btn.set_active(True)
            self.show_gridlines(grid_btn)

    def set_name(self, name):
        self.log_list.change_name(name)

    def fill(self, *args):
        if self.log_list.table:
            self.exec_sens(True)
            self.log_list.execute(self.filter_logs.get_sql(),
                                  self.loader.get_auto_lid())
            self.exec_sens(False)

    def cancel(self, *args):
        db.interrupt()

    def show_query(self, button):
        if button.get_active():
            self.box.remove(self.logs_window)
            self.paned.pack1(self.logs_window, True, False)
            self.paned.pack2(self.loader, False, False)
            self.paned.set_position(575)
            self.box.pack_end(self.paned)
        else:
            self.paned.remove(self.logs_window)
            self.paned.remove(self.loader)
            self.box.remove(self.paned)
            self.box.pack_end(self.logs_window)
        self.show_all()

    def show_gridlines(self, button):
        if button.get_active():
            self.log_list.view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
        else:
            self.log_list.view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)

    def show_log_window(self, *args):
        if self.log_list.model:
            self.exec_sens(True)
            view = self.log_list.view
            selection = view.get_selection()
            (model, pathlist) = selection.get_selected_rows()
            try:
                if pathlist:
                    if len(pathlist) > 1:
                        SeveralLogsWindow(self.log_list,
                                          self.log_list.model.get_iter(pathlist[0]),
                                          selection, self.exec_sens)
                    else:
                        selection.set_mode(gtk.SELECTION_SINGLE)
                        LogWindow(self.log_list, self.log_list.model.get_iter(pathlist[0]),
                                    selection, self.exec_sens)
                        selection.set_mode(gtk.SELECTION_MULTIPLE)
            except ValueError:
                selection.set_mode(gtk.SELECTION_MULTIPLE)
            self.exec_sens(False)

    def exec_sens(self, start):
        self.break_btn.set_sensitive(start)
        self.ntb.set_sens((not start))

    def text_grab_focus(self, *args):
        self.filter_logs.txt.grab_focus()

    @property
    def get_view(self):
        return self.log_list.view
