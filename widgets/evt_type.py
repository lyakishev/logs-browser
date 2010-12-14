import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
from common_filter import CommonFilter

class EventTypeFilter(CommonFilter):
    def __init__(self, event_types, default):
        super(EventTypeFilter, self).__init__("Type")
        self.event_box = gtk.VBox()
        self.evt_checkboxes = {}
        for evt in event_types.itervalues():
            self.evt_checkboxes[evt]=gtk.CheckButton(label=evt)
            if default in evt:
                self.evt_checkboxes[evt].set_active(True)
        for chb in self.evt_checkboxes.itervalues():
            self.event_box.pack_start(chb, False, False, 1)
        self.add(self.event_box)
        self.set_start_active(True)

    @property
    def get_event_types(self):
        types = []
        for t in self.evt_checkboxes:
            if self.evt_checkboxes[t].get_active() == True:
                types.append(t)
        return types
