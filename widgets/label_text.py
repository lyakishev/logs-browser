import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import pango


class LabelText(gtk.Expander):
    def __init__(self):
        super(LabelText, self).__init__("Information")

        self.label = gtk.Label()
        self.label.set_markup('Double-click for typing <b>information</b>.')
        self.label.set_alignment(0.01, 0)
        self.label.set_line_wrap(True)
        self.textview = gtk.TextView()
        self.textview.set_wrap_mode(gtk.WRAP_CHAR)
        self.buf = self.textview.get_buffer()
        self.event = gtk.EventBox()
        
        self.event.add(self.label)
        self.event.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.event.connect("button-press-event", self.to_entry)
        self.textview.connect("focus-out-event", self.to_label)
    
        self.add(self.event)
        
    def to_entry(self, widget, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.buf.set_text(self.label.get_label())
            self.remove(self.event)
            self.add(self.textview)
            self.textview.grab_focus()
            self.show_all()

    def to_label(self, *args):
        text = self.buf.get_text(self.buf.get_start_iter(),
                                 self.buf.get_end_iter())
        self.label.set_markup(text)
        self.remove(self.textview)
        self.add(self.event)
        txt = self.label.get_text()
        self.set_label(txt[:80]+"..." if len(txt)>80 else txt)
        label_set_autowrap(self.label)
        self.show_all()


#From https://fedorahosted.org/python-slip/browser/slip/gtk/tools.py:

def label_set_autowrap(widget):
    """Make labels automatically re-wrap if their containers are resized.
    Accepts label or container widgets."""

    if isinstance(widget, gtk.Container):
        children = widget.get_children()
        for i in xrange(len(children)):
            label_set_autowrap(children[i])
    elif isinstance(widget, gtk.Label) and widget.get_line_wrap():
        widget.connect_after("size-allocate", __label_size_allocate)


def __label_size_allocate(widget, allocation):
    """Callback which re-allocates the size of a label."""

    layout = widget.get_layout()

    (lw_old, lh_old) = layout.get_size()

    # fixed width labels

    if lw_old / pango.SCALE == allocation.width:
        return

    # set wrap width to the pango.Layout of the labels ###

    layout.set_width(allocation.width * pango.SCALE)
    (lw, lh) = layout.get_size()

    if lh_old != lh:
        widget.set_size_request(-1, lh / pango.SCALE)

        
        
        


        
