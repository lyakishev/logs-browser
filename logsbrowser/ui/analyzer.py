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
import gtk, gobject, gio, glib
from db_procs import *

class PLSQL_Analyzer(object):
    def __init__(self, proc, user=None, instance=None):
        self.pa = ProcAnalyzer(proc,
                     "tf2_cust/cust@heine")
	w = gtk.Window()
	w.set_default_size(800,600)
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
	self.t = gtk.TextView()
	self.t.set_wrap_mode(gtk.WRAP_WORD)
	self.buf = self.t.get_buffer()
        end = self.buf.get_end_iter()
        self.buf.insert(end, self.pa.proc_source)
	sw.add(self.t)
	w.add(sw)
	w.show_all()
