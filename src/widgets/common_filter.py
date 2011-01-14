import pygtk
pygtk.require("2.0")
import gtk, gobject, gio

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
