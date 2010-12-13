import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from common_filter import CommonFilter

class QuantityFilter(CommonFilter):
    def __init__(self):
        super(LastFilter, self).__init__("Quantity")
        self.last_label = gtk.Label("Last")
        self.last_adjustment = gtk.Adjustment(value=3, lower=1, upper=100, step_incr=1)
        self.last_spinbutton = gtk.SpinButton(adjustment=self.last_adjustment)
        self.last_box = gtk.HBox()
        self.last_box.pack_start(self.last_label, False, False)
        self.last_box.pack_start(self.last_spinbutton, False, False,20)
        self.add(self.last_box)
