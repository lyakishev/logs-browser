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

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
try:
    from utils.mouse_click import DetectClick
except ImportError:
    pass
from multiprocessing import Value
from utils.net_time import get_true_time


class StatusIcon:
    def __init__(self, date_filter, window):
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_YES)
        self.statusicon.connect("activate", self.change_mode)
        self.statusicon.set_tooltip("Log Viewer")
        self.record = 0
        self.date_filter = date_filter
        self.window = window
        self.hide = 0
        self.active = True

    def change_mode(self, *args):
        now = get_true_time()
        if self.record:
            self.statusicon.set_from_stock(gtk.STOCK_YES)
            self.date_filter.fromto_option.to_date.set_date(now)
            self.record = 0
        else:
            self.statusicon.set_from_stock(gtk.STOCK_NO)
            if self.active:
                ct = Value('d', 0.0)
                p = DetectClick(ct)
                p.start()
                p.join()
                self.date_filter.fromto_option.from_date.set_date(ct.value)
            else:
                self.date_filter.fromto_option.from_date.set_date(now)
            self.record = 1

    def hide_main_window(self, *args):
        self.window.hide()

    def show_main_window(self, *args):
        self.window.show()
