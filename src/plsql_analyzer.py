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
