# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from logwindow import LogWindow
from query import Query
from logwindow import SeveralLogsWindow
from datetime import datetime
import pango
import os
from operator import mul, itemgetter
from db.engine import create_new_table, get_msg, execute, set_break,\
                        DBException, drop, set_callback, check_break,\
                        interrupt
from utils.hash import hash_value
from dialogs import merror

def callback():
    if check_break():
        set_break(False)
        interupt()
    while gtk.events_pending():
        gtk.main_iteration()

set_callback(callback)


class LogList(object):
    
    sql_context = {}

    def __init__(self):
        self.view = gtk.TreeView()
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.model = None
        self.columns = []
        self.headers = []
        self.fts = True
        self.name = ""
        self.table = ""

    def change_name(self, name):
        try:
            self.sql_context.pop(self.name)
        except KeyError:
            pass
        finally:
            self.name = name
            self.sql_context[self.name] = self.table

    def execute(self, sql):
        self.view.freeze_child_notify()
        self.view.set_model(None)
        try:
            desc, rows = execute(sql, self.get_context())
        except DBException, e:
            merror(str(e))
            rows = None
        if rows:
            self.headers = map(itemgetter(0), desc)
            cols = [gobject.TYPE_STRING for i in self.headers]
            self.model = gtk.ListStore(*cols)
            self.build_view(self.headers)
            for row in iter(rows):
                self.model.append(row)
            self.view.set_model(self.model)
        self.view.thaw_child_notify()

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
            if header == 'rows_for_log_window':
                self.rflw = number
            if header in ('rows_for_log_window', 'bgcolor'):
                col.set_visible(False)

    def clear(self):
        self.sql_context.pop(self.name)
        if self.model:
            self.model.clear()
        if self.table:
            drop(self.table)

    def get_context(self):
        con = self.sql_context.copy()
        con.update({"this": self.table})
        return con
        
    def new_logs(self, index):
        self.clear()
        self.table = hash_value(datetime.now())
        self.sql_context[self.name] = self.table
        create_new_table(self.table, index)
        self.fts = index


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

    def set_name(self, name):
        self.log_list.change_name(name)

    def fill(self, *args):
        self.break_btn.set_sensitive(True)
        self.ntb.set_sens(False)
        self.log_list.execute(self.filter_logs.get_sql())
        self.ntb.set_sens(True)
        self.break_btn.set_sensitive(False)

    def cancel(self, *args):
        set_break(True)

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
            selection.set_mode(gtk.SELECTION_SINGLE)
            LogWindow(self.log_list, self.log_list.model.get_iter(pathlist[0]),
                        selection)
            selection.set_mode(gtk.SELECTION_MULTIPLE)
            

    def text_grab_focus(self, *args):
        self.filter_logs.text.grab_focus()

    @property
    def get_view(self):
        return self.log_list.view
