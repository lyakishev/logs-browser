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


class CommonFilter(gtk.Frame):
    def __init__(self, name):
        super(CommonFilter, self).__init__()
        self.check_filter = gtk.CheckButton(name)
        self.check_filter.connect("toggled", self.filter_sens)
        self.set_label_widget(self.check_filter)

    def filter_sens(self, *args):
        if self.check_filter.get_active():
            self.get_children()[0].set_sensitive(True)
        else:
            self.get_children()[0].set_sensitive(False)

    def get_active(self):
        return self.check_filter.get_active()

    def set_start_active(self, active):
        self.check_filter.set_active(active)
        self.filter_sens()
