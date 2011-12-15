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

# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
from logwindow import LogWindow, SeveralLogsWindow
from query import Query, QueryLoader
from datetime import datetime
import pango
import os
from operator import mul, itemgetter, setitem
import db.engine as db
from db.parse import process
from utils.hash import hash_value, sql_to_hash
from utils.xmlmanagers import QueriesManager
from dialogs import merror
import glib
from itertools import cycle
import config
from cellrenderercolors import CellRendererColors
from string import Template
from utils.profiler import time_it, profile
from utils.colors import ColorError
from panedbox import PanedBox
from toolbar import Toolbar
import re
from filedialogs import save_file_dialog, save_files_to_dir_dialog

bad_chars = re.compile('[?|:*"><]')

def callback():
    while gtk.events_pending():
        gtk.main_iteration()

db.set_callback(callback)

class FTemplate(Template):
    delimiter = '#'

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
        self.words_hl = ""
        self.name = ""
        self.table = ""
        self.from_ = ""
        self.cached_queries = []
        self.bgcolorsn = []
        self.view.connect("button-press-event", self.copy_cell)

    def copy_cell(self, view, event):
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            if path:
                row = self.model.get_iter(path[0])
                col = [n for n,c in enumerate(self.columns) if c == path[1]][0]
                if col:
                    value = self.model.get_value(row, col)
                    clipboard = gtk.clipboard_get("CLIPBOARD")
                    clipboard.set_text(value)

    def visible_rows(self):
        visible_columns = [n for n, c in enumerate(self.columns) if c.get_visible()]
        for row in self.model:
            yield [c for n,c in enumerate(row) if n in visible_columns]
        
    def change_name(self, name):
        try:
            self.sql_context.pop(self.name)
        except KeyError:
            pass
        finally:
            self.name = name
            self.sql_context[self.name] = self.table

    def execute(self, sql_templ, from_constr, auto_lid):
        query = sql_templ[0]
        filter_ = sql_templ[1]
        context = self.get_context()
        fcontext = {}
        for k in context:
            if k == 'this':
                fcontext[k] = Template(filter_).safe_substitute({'table': '$'+from_constr})
            else:
                fcontext[k] = Template(filter_).safe_substitute({'table': '$'+k})
        fquery = FTemplate(query).safe_substitute(fcontext)
        try:
            sql, words_hl, self.from_ = process(fquery, context, auto_lid, self.fts)
        except Exception as e:
            merror(str(e))
            return
        self.view.freeze_child_notify()
        self.view.set_model(None)
        sql_hash = sql_to_hash(sql)
        model = self._cache.get(sql_hash)
        if model:
            self.model = model[0]
            self.headers = model[1]
            self.words_hl = model[2]
            self.build_view(self.headers)
            self.view.set_model(self.model)
            self.view.thaw_child_notify()
            return
        else:
            try:
                desc, rows = db.execute(sql)
            except db.DBException as e:
                merror(str(e))
                rows = None
            else:
                self.words_hl = words_hl
            if rows:
                self.headers = map(itemgetter(0), desc)
                cols = [gobject.TYPE_STRING for i in self.headers]
                self.model = gtk.ListStore(*cols)
                self.build_view(self.headers)
                for row in iter(rows):
                    self.model.append(row)
                if 'bgcolor' in self.headers:
                    bgcolor = self.headers.index('bgcolor')
                    white = set(["#fff", "None"])
                    colorcols = [n for n, c in enumerate(self.headers)
                                             if c.startswith('bgcolor')]
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
                self._cache[sql_hash] = (self.model, self.headers, words_hl)
                self.cached_queries.append(sql_hash)
                self.view.set_model(self.model)
            self.view.thaw_child_notify()

    def concat_row_vals(self, row):
        name_parts = []
        for n, name in enumerate(row):
            if name and n != self.rflw and n not in self.bgcolorsn:
                if os.sep in name:
                    name = os.path.basename(name)
                name_parts.append(bad_chars.sub('-', name))
        pathname = '_'.join(name_parts)
        path, ext = os.path.splitext(pathname)
        if ext in ('.txt', '.log'):
            return pathname
        else:
            return "%s.log" % pathname

    def get_row_msg_action(self, path):
        row = self.model[path]
        return self.concat_row_vals(row), lambda: db.get_log(row[self.rflw], self.from_)

    def build_view(self, args):
        self.bgcolorsn = []
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
                self.bgcolorsn.append(number)
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

    def up_color(self, color=None):
        try:
            bgcolor = self.headers.index('bgcolor')
        except ValueError:
            return
        else:
            selection = self.view.get_selection()
            selection.set_mode(gtk.SELECTION_SINGLE)
            (model, iter_) = selection.get_selected()
            if iter_:
                path = model.get_string_from_iter(iter_)
                path = int(path) - 1
            else:
                path = model.iter_n_children(None) - 1
            if path >= 0:
                if not color:
                    clause = lambda p: model[p][bgcolor] == '#fff'
                else:
                    if color == '#fff':
                        selection.set_mode(gtk.SELECTION_MULTIPLE)
                        return
                    clause = lambda p: color not in model[p][bgcolor]
                while clause(path):
                    path -= 1
                    if path < 0:
                        break
                else:
                    selection.select_path(path)
                    self.view.scroll_to_cell(path, use_align=True, row_align=0.5)
            selection.set_mode(gtk.SELECTION_MULTIPLE)

    def down_color(self, color=None):
        try:
            bgcolor = self.headers.index('bgcolor')
        except ValueError:
            return
        else:
            selection = self.view.get_selection()
            selection.set_mode(gtk.SELECTION_SINGLE)
            (model, iter_) = selection.get_selected()
            if iter_:
                iter_ = model.iter_next(iter_)
            else:
                iter_ = model.get_iter_first()
            if iter_:
                if not color:
                    clause = lambda it: model.get_value(it, bgcolor) == '#fff'
                else:
                    if color == '#fff':
                        selection.set_mode(gtk.SELECTION_MULTIPLE)
                        return
                    clause = lambda it: color not in model.get_value(it, bgcolor)
                while clause(iter_):
                    iter_ = model.iter_next(iter_)
                    if not iter_:
                        break
                else:
                    selection.select_iter(iter_)
                    self.view.scroll_to_cell(int(model.get_string_from_iter(iter_)),
                                             use_align=True, row_align=0.5)
            selection.set_mode(gtk.SELECTION_MULTIPLE)


class LogsListWindow(gtk.Frame):
    def __init__(self, ntb):
        super(LogsListWindow, self).__init__()
        self.log_list = LogList()
        self.log_list.view.connect('row-activated', self.show_log_window)
        self.logs_window = gtk.ScrolledWindow()
        self.logs_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.logs_window.add(self.log_list.view)

        toolbar = Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        
        exec_btn = toolbar.append_button(gtk.STOCK_EXECUTE, self.fill)

        self.break_btn = toolbar.append_button(gtk.STOCK_CANCEL, self.cancel)

        toolbar.append_sep()
        toolbar.append_togglebutton(gtk.STOCK_PAGE_SETUP, self.show_query,
                                    "Edit Query")
        toolbar.append_sep()
        lwin_btn = toolbar.append_button(gtk.STOCK_FILE, self.show_log_window,
                              "Show Log(s)")
        slog_btn = toolbar.append_button(gtk.STOCK_SAVE, self.save_logs,
                              "Save Log(s)")
        toolbar.append_sep()
        grid_btn = toolbar.append_togglebutton(gtk.STOCK_UNDERLINE, self.show_gridlines,
                                    "Grid Lines")

        toolbar.append_sep()
        toolbar.append_button(gtk.STOCK_GO_UP, lambda btn: self.log_list.up_color())
        toolbar.append_button(gtk.STOCK_GO_DOWN, lambda btn: self.log_list.down_color())
        toolbar.append_sep()

        exp_btn = toolbar.append_button(gtk.STOCK_COPY, self.csv_export,
                              "Export...")

        self.qm = QueriesManager(config.QUERIES_FILE)
        self.filter_logs = Query(self.log_list)
        self.loader = QueryLoader(self.filter_logs, self.qm, ntb.notify_loaders)

        self.box = PanedBox(self.show_all, 500)
        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.logs_window, True, True)
        self.box.paned_pack(self.loader)

        self.add(self.box)
        self.show_all()
        self.break_btn.set_sensitive(False)

        self.sens_list = [exec_btn, lwin_btn, slog_btn, exp_btn] + self.filter_logs.sens_list
        self.ntb = ntb

        if config.GRID_LINES:
            grid_btn.set_active(True)
            self.show_gridlines(grid_btn)

    def get_loader(self):
        return self.loader

    @time_it
    def save_logs(self, *args):
        actions = self.get_selected()
        if len(actions) > 1:
            save_files_to_dir_dialog(actions, self.ntb.set_sens, self.ntb.progress)
        else:
            save_file_dialog(actions, self.ntb.set_sens, self.ntb.progress)
        
    def csv_export(self, *args):
        fchooser = gtk.FileChooserDialog("Export logs list...", None,
            gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
        fchooser.set_current_name("logslist.csv")
        response = fchooser.run()
        if response == gtk.RESPONSE_OK:
            import csv
            path = fchooser.get_filename()
            with open(path, 'wb') as f:
                writer = csv.writer(f)
                writer.writerows(self.log_list.visible_rows())
        fchooser.destroy()

    def set_name(self, name):
        self.log_list.change_name(name)

    def fill(self, *args):
        self.exec_sens(True)
        self.filter_logs.unselect()
        self.log_list.execute(self.loader.get_query(),
                              self.loader.get_from(),
                              self.loader.get_auto_lid())
        self.exec_sens(False)

    def cancel(self, *args):
        db.interrupt()

    def show_query(self, button):
        self.box.change_box(button.get_active())

    def show_gridlines(self, button):
        if button.get_active():
            self.log_list.view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
        else:
            self.log_list.view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)

    def get_selected(self):
        view = self.log_list.view
        selection = view.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        return dict(map(self.log_list.get_row_msg_action, pathlist))

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
                                          selection, self.exec_sens,
                                          self.log_list.words_hl)
                    else:
                        selection.set_mode(gtk.SELECTION_SINGLE)
                        LogWindow(self.log_list, self.log_list.model.get_iter(pathlist[0]),
                                    selection, self.exec_sens, self.log_list.words_hl)
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
