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
from colorparser import HighlightSyntaxTextView
import pango
import traceback
from dialogs import merror
from db.engine import get_msg, DBException
import config
from textview import SearchHighlightTextView
from toolbar import Toolbar
from panedbox import PanedBox

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
        updown_btns = gtk.VButtonBox()
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
        updown_btns.pack_start(up)
        updown_btns.pack_start(down)
        self.pack_start(updown_btns, False, False, padding=30)

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

        self.popup = gtk.Window()
        self.popup.set_default_size(config.WIDTH_LOG_WINDOW, config.HEIGHT_LOG_WINDOW)

        self.box = PanedBox(self.popup.show_all,
                config.HEIGHT_LOG_WINDOW - config.HEIGHT_LOG_WINDOW/4)

        self.info_box = Info(self.set_next, self.set_prev)
        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.log_text = SearchHighlightTextView()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_WORD)
        self.scr.add(self.log_text)

        toolbar = Toolbar()
        toolbar.append_button(gtk.STOCK_OPEN, self.open_file)
        toolbar.append_button(gtk.STOCK_SAVE, self.open_file)
        toolbar.append_button(gtk.STOCK_COPY, self.open_file)

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

        toolbar.append_button(gtk.STOCK_APPLY, self.highlight)

        toolbar.append_sep()

        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)

        self.highlighter = HighlightSyntaxTextView()
        scrh = gtk.ScrolledWindow()
        scrh.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrh.add(self.highlighter)

        self.box.pack_start(self.info_box, False, False, padding=10)
        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.scr)
        self.box.paned_pack(scrh)

        self.popup.add(self.box)

        self.get_syntax_from_config()
        try:
            self.set_log()
        except DBException as e:
            merror(str(e))
            self.popup.destroy()
        else:
            self.fill_highlight_combo()
            self.popup.show_all()

    def get_syntax_from_config(self):
        with open(config.SYNTAX_CFG) as f:
            conf = f.read()
            self.config = eval(conf)           #TODO: CHANGE IT!!
            f.close()

    def fill_highlight_combo(self):
        syntax = self.config.keys()
        self.syntax.append_text("from table")
        self.syntax.append_text("-------")
        for item in syntax:
            self.syntax.append_text(item)
        self.config.update({"from table": self.from_table_hl})
        self.syntax.set_active(0)

    def change_syntax(self, *args):
        syntax = self.syntax.get_active_text()
        c_syntax = self.config.get(syntax, "")
        self.highlighter.txt_buff.set_text(c_syntax)
        self.highlight()

    def highlight(self, *args):
        self.log_text.highlight(self.highlighter.get_syntax())

    def save_to_file(self, *args):
        fchooser = gtk.FileChooserDialog("Save logs to file...", None,
            gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
        fchooser.set_current_name("_".join([os.path.basename(f) for f in
                                            self.files]))
        response = fchooser.run()
        if response == gtk.RESPONSE_OK:
            path = fchooser.get_filename()
            f = open(path.decode('utf8'), "w")
            f.write(self.get_text())
            f.close()
        fchooser.destroy()

    def open_file(self, *args):
        for f in self.files:
            subprocess.Popen("%s %s" % (config.EXTERNAL_LOG_VIEWER, f))

    def set_log(self):
        rows = self.model.get_value(self.iter_, self.loglist.rflw)
        select = get_msg(rows, self.loglist.from_)
        self.log_text.write_from_iterable(select[4])
        self.log_text.highlight(self.highlighter.get_syntax())
        self.log_text.grab_focus()
        self.files = set(select[3])
        date_, logname = self.info_box.set_info(select[0], select[1], select[2], self.files)
        self.popup.set_title("Log: %s %s" % (logname.replace('\n', ','),
                                             date_))

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
        self.popup.set_sensitive(False)
        self.sens_func(True)
        try:
            self.set_log()
        except DBException as e:
            merror(str(e))
            self.selection.select_path(int(path))
            self.view.scroll_to_cell(int(path))
            self.iter_ = self.model.get_iter_from_string(path)
        finally:
            self.popup.set_sensitive(True)
            self.sens_func(False)
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
            self.popup.set_sensitive(False)
            self.sens_func(True)
            try:
                self.set_log()
            except DBException as e:
                merror(str(e))
                self.selection.select_path(int(path))
                self.view.scroll_to_cell(int(path))
                self.iter_ = self.model.get_iter_from_string(path)
            finally:
                self.popup.set_sensitive(True)
                self.sens_func(False)
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)


class SeveralLogsWindow(LogWindow):
    def __init__(self, loglist, iter, sel, sens_func, from_table_hl):
        LogWindow.__init__(self, loglist, iter, sel, sens_func, from_table_hl)
        self.info_box.remove(self.updown_btns)

    def fill(self):
        model, pathlist = self.selection.get_selected_rows()
        dates = []
        text = []
        types = []
        lognames = []
        self.files = []
        prev_f = ""
        for p in reversed(pathlist):
            iter_ = model.get_iter(p)
            rows = self.model.get_value(iter_, self.loglist.rflw)
            select = get_msg(rows, self.loglist.from_)
            dates.extend(select[0])
            lognames.extend(select[1])
            types.extend(select[2])
            files = select[3]
            txt = select[4]
            for n,f in enumerate(files):
                if prev_f == f:
                    text.append(txt[n])
                else:
                    text.append("%s:\n\n%s" % (f, txt[n]))
                prev_f = f
            self.files.extend(files)
        self.files = set(self.files)
        self.txt = "\n".join(text)
        type_ = ("ERROR" in types) and '<span foreground="red">ERROR</span>' or ""
        logname_ = "\n".join(set(lognames))
        if len(dates) > 1:
            start = min(dates).strftime("%H:%M:%S.%f %d.%m.%Y")
            end = max(dates).strftime("%H:%M:%S.%f %d.%m.%Y")
            date_ = "%s - %s" % (start, end)
        else:
            date_ = select[0][0].strftime("%H:%M:%S.%f %d.%m.%Y")
        self.filling(date_,logname_,type_)
