import pygtk
import gtk, gobject, gio
import glib
import os

class FileMonitor():

    def __init__(self, file_):
        self.file_ = file_
	w = gtk.Window()
	w.set_default_size(800,600)
	w.connect("destroy", self.destroy)
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
	self.t = gtk.TextView()
	self.t.set_wrap_mode(gtk.WRAP_WORD)
	self.buf = self.t.get_buffer()
	self.new_tag = self.buf.create_tag("new", foreground="red")
	self.f_size = os.path.getsize(file_)
	self.gf = gio.File(file_)
	self.m = self.gf.monitor(gio.FILE_MONITOR_NONE, None)
	self.m.connect('changed', self.file_changed)
	sw.add(self.t)
	w.add(sw)
	w.show_all()


    def destroy(self, *args):
        import sys
	sys.exit()
    	gtk.main_quit()

    def file_changed(self, m, f1, f2, evt_type):
	#print "changed"
        path = f1.get_path()
        new_size = os.path.getsize(path)
        f = open(path)
        f.seek(self.f_size)
        c = f.read()
        f.close()
        end = self.buf.get_end_iter()
        self.buf.insert(end, c)
        self.f_size = new_size
	new_end = self.buf.get_end_iter()
        self.t.scroll_to_iter(new_end,0)
	#start = self.buf.get_start_iter()
	#self.buf.remove_all_tags(start, end)
	#self.buf.apply_tag(self.new_tag, end, new_end)

fm = FileMonitor(r"\\msk-portal-01\forislog\Ncih\back-end-all.log")
ml = glib.MainLoop()
ml.run()
