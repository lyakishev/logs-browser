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

#-*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import re
import xml.dom.minidom
import os
import subprocess
from highlighter import Highlighter
import pango
import traceback
from dialogs import merror
from db.engine import get_msg, DBException
import config
from textview import SearchHighlightTextView
from toolbar import Toolbar
from panedbox import PanedBox
from utils.xmlmanagers import SyntaxManager
from utils.pxml import prettify_xml
from dialogs import save_dialog
from itertools import groupby, chain
from filedialogs import save_file_dialog

class Info(gtk.HBox):
    def __init__(self, next_, prev_):
        gtk.HBox.__init__(self)
        self.info_label = gtk.Label()
        self.info_label.set_selectable(True)
        self.open_label = gtk.Label()
        self.open_label.set_selectable(True)
        open_info_box = gtk.VBox()
        self.pack_start(open_info_box)
        open_info_box.pack_start(self.info_label)
        open_info_box.pack_start(self.open_label)
        self.updown_btns = gtk.VButtonBox()
        up = gtk.Button()
        up_im = gtk.Image()
        up_im.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_BUTTON)
        up.add(up_im)
        up.connect("clicked", next_)
        down = gtk.Button()
        dwn_im = gtk.Image()
        dwn_im.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_BUTTON)
        down.add(dwn_im)
        down.connect("clicked", prev_)
        self.updown_btns.pack_start(up)
        self.updown_btns.pack_start(down)
        self.pack_start(self.updown_btns, False, False, padding=30)

    def set_info(self, dates, lognames, types, files):
        self.open_label.set_text("\n".join(files))
        type_ = ("ERROR" in types) and '<span foreground="red">ERROR</span>' or ""
        logname_ = "\n".join(set(lognames))
        date_ = self.get_min_max_dates(dates)
        self.info_label.set_markup('<big><b>%s</b></big>\n%s\n%s\n' % (date_,
                                                                     logname_,
                                                                     type_))
        return date_, logname_

    def get_min_max_dates(self, dates):
        start = min(dates)
        end = max(dates)
        if start != end:
            date_ = "%s - %s" % (start, end)
        else:
            date_ = start
        return date_

class LogWindow:
    def __init__(self, loglist, iter_, sel, sens_func, from_table_hl):
        self.from_table_hl = from_table_hl
        self.model = loglist.model
        self.view = loglist.view
        self.loglist = loglist
        self.selection = sel
        self.sens_func = sens_func
        self.iter_ = iter_

        self.syntax_manager = SyntaxManager(config.SYNTAX_CFG)

        self.popup = gtk.Window()
        self.popup.set_default_size(config.WIDTH_LOG_WINDOW, config.HEIGHT_LOG_WINDOW)

        self.box = PanedBox(self.popup.show_all,
                config.HEIGHT_LOG_WINDOW - 215)

        self.info_box = Info(self.set_next, self.set_prev)
        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.log_text = SearchHighlightTextView()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_CHAR)
        self.scr.add(self.log_text)

        toolbar = Toolbar()
        toolbar.append_button(gtk.STOCK_OPEN, self.open_file)
        toolbar.append_button(gtk.STOCK_SAVE, self.save_to_file)
        toolbar.append_button(gtk.STOCK_COPY, self.log_text.copy)

        toolbar.append_sep()
        
        toolbar.append_item(gtk.Label("Find:"))

        re_toggle = gtk.CheckButton("regexp")
        re_toggle.connect_after("toggled", self.log_text.re_toggled_search)

        find_entry = gtk.Entry()
        find_entry.connect("changed", self.log_text.changed_search,
                                        re_toggle.get_active)
        toolbar.append_item(find_entry)
        toolbar.append_button(gtk.STOCK_GO_BACK, self.log_text.prev_search)
        toolbar.append_button(gtk.STOCK_GO_FORWARD, self.log_text.next_search)

        toolbar.append_item(re_toggle)
        toolbar.append_sep()

        toolbar.append_togglebutton(gtk.STOCK_SELECT_COLOR,
                                lambda btn: self.box.change_box(btn.get_active()))

        self.syntax = gtk.combo_box_new_text()
        self.syntax.connect("changed", self.change_syntax)
        toolbar.append_item(self.syntax)


        toolbar.append_sep()

        self.pretty_btn = toolbar.append_togglebutton(gtk.STOCK_CONVERT, self.pretty)

        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)

        self.highlighter = Highlighter(self.highlight,
                                        self.save_syntax,
                                        self.save_syntax_as)

        self.box.pack_start(self.info_box, False, False, padding=10)
        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.scr)
        self.box.paned_pack(self.highlighter)

        self.popup.add(self.box)

        try:
            self.set_log()
        except DBException as e:
            merror(str(e))
            self.popup.destroy()
        else:
            self.fill_highlight_combo()
            self.popup.show_all()

    def pretty(self, toggle):
        self.sens_func(True)
        if toggle.get_active():
            self.log_text.transform(prettify_xml)
        else:
            self.log_text.restore()
        self.highlight()
        self.sens_func(False)

    def fill_highlight_combo(self):
        model = self.syntax.get_model()
        if model:
            model.clear()
        syntax = self.syntax_manager.syntaxes.keys()
        self.syntax.append_text("from table")
        self.syntax.append_text("-------")
        for item in syntax:
            self.syntax.append_text(item)
        self.syntax.set_active(0)

    def change_syntax(self, *args):
        syntax = self.syntax.get_active_text()
        if syntax == "from table":
            c_syntax = self.from_table_hl
        else:
            c_syntax = self.syntax_manager.syntaxes.get(syntax, "")
        self.highlighter.txt_buff.set_text(c_syntax)
        self.highlight()

    def save_syntax(self, *args):
        syntax_name = self.syntax.get_active_text()
        if syntax_name != 'from table':
            syntax = self.highlighter.get_text()
            self.syntax_manager.add_syntax(syntax_name, syntax)
            self.highlight()

    def set_active_syntax(self, syntax_name):
        for n, r in enumerate(self.syntax.get_model()):
            if r[0] == syntax_name:
                self.syntax.set_active(n)
                return

    def save_syntax_as(self, *args):
        syntax = self.highlighter.get_text()
        syntax_name = save_dialog()
        self.syntax_manager.add_syntax(syntax_name, syntax)
        self.fill_highlight_combo()
        self.set_active_syntax(syntax_name)


    def highlight(self, *args):
        self.log_text.highlight(self.highlighter.get_syntax())

    def save_to_file(self, *args):
        name = "_".join([os.path.basename(f) for f in self.files])
        save_file_dialog({name: self.log_text.get_text})

    def open_file(self, *args):
        for f in self.files:
            subprocess.Popen("%s %s" % (config.EXTERNAL_LOG_VIEWER, f))

    def set_log(self):
        self.sens_func(True)
        self.popup.set_sensitive(False)
        self.pretty_btn.set_active(False)
        rows = self.model.get_value(self.iter_, self.loglist.rflw)
        select = get_msg(rows, self.loglist.from_)
        self.log_text.write_from_iterable(select[4])
        self.log_text.highlight(self.highlighter.get_syntax())
        self.log_text.grab_focus()
        self.files = set(select[3])
        date_, logname = self.info_box.set_info(select[0], select[1], select[2], self.files)
        self.popup.set_title("Log: %s %s" % (logname.replace('\n', ','),
                                             date_))
        self.popup.set_sensitive(True)
        self.sens_func(False)

    def set_prev(self, *args):
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        path = self.model.get_string_from_iter(self.iter_)
        if path == 0:
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)
            return None
        prevPath = int(path) + 1
        try:
            self.iter_ = self.model.get_iter_from_string(str(prevPath))
        except ValueError:
            return
        self.selection.select_path(prevPath)
        self.view.scroll_to_cell(prevPath)
        try:
            self.set_log()
        except DBException as e:
            merror(str(e))
            self.selection.select_path(int(path))
            self.view.scroll_to_cell(int(path))
            self.iter_ = self.model.get_iter_from_string(path)
        finally:
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    def set_next(self, *args):
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        path = self.model.get_string_from_iter(self.iter_)
        if path == 0:
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)
            return None
        prevPath = int(path) - 1
        if prevPath >= 0:
            self.iter_ = self.model.get_iter_from_string(str(prevPath))
            self.selection.select_path(prevPath)
            self.view.scroll_to_cell(prevPath)
            try:
                self.set_log()
            except DBException as e:
                merror(str(e))
                self.selection.select_path(int(path))
                self.view.scroll_to_cell(int(path))
                self.iter_ = self.model.get_iter_from_string(path)
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)


class SeveralLogsWindow(LogWindow):
    def __init__(self, loglist, iter, sel, sens_func, from_table_hl):
        LogWindow.__init__(self, loglist, iter, sel, sens_func, from_table_hl)
        self.info_box.remove(self.info_box.updown_btns)

    def set_log(self):
        self.sens_func(True)
        self.popup.set_sensitive(False)
        self.pretty_btn.set_active(False)
        model, pathlist = self.selection.get_selected_rows()
        dates = []
        files_text = []
        types = []
        lognames = []
        self.files = []
        for p in reversed(pathlist):
            iter_ = model.get_iter(p)
            rows = self.model.get_value(iter_, self.loglist.rflw)
            select = get_msg(rows, self.loglist.from_)
            dates.extend(select[0])
            lognames.append(select[1])
            types.append(select[2])
            files_text.append((select[3], select[4]))
        prev_f = ""
        for f_gen, msg_gen in files_text:
            for f, msg in zip(f_gen, msg_gen):
                if f != prev_f:
                    text = "%s%s" % (os.linesep if prev_f else "",
                                    "{1}:{0}{0}{2}".format(os.linesep, f, msg))
                    prev_f = f
                    self.files.append(f)
                else:
                    text = msg
                self.log_text.txt_buff.insert_at_cursor(text)
        self.files = set(self.files)
        self.info_box.set_info(dates, chain.from_iterable(lognames),
                                      chain.from_iterable(types), self.files)
        self.popup.set_sensitive(True)
        self.sens_func(False)

