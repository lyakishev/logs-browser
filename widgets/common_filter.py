import pygtk
pygtk.require("2.0")
import gtk, gobject, gio

class CommonFilter(gtk.Frame):
    def __init__(self, name):
        self.check_filter = gtk.CheckButton(name)
        self.check_filter.connect("toggled", filter_sens)
        self.set_label_widget(self.check_filter)

    def filter_sens(self, *args):
        if self.check_filter.get_active():
            self.children[0].set_sensitive(True)
        else:
            self.children[0].set_sensitive(False)
