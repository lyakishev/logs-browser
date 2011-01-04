import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import re
import pango

cparser = re.compile(r"(#[a-fA-F0-9]{3,}):")

class ColorParser(gtk.HBox):
    def __init__(self, model, view):
        super(ColorParser, self).__init__()

        self.model = model
        self.view = view

        self.text = gtk.TextView()
        self.buf = self.text.get_buffer()
        self.filter_button = gtk.Button("Filter")
        self.color_button = gtk.Button("Color")
        self.hide_other = gtk.CheckButton("Hide other")
        
        self.button_box = gtk.VButtonBox()
        self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.button_box.pack_start(self.filter_button)
        self.button_box.pack_start(self.color_button)
        self.button_box.pack_start(self.hide_other)

        self.pack_start(self.text, True, True, 2)
        self.pack_start(self.button_box, False, False)

        self.filter_button.connect("clicked", self.filter_logs)
        self.color_button.connect("clicked", self.change_color)

        self.color_tags = {}
        self.bold_tag = self.buf.create_tag("bold", weight=pango.WEIGHT_BOLD)

    def filter_logs(self, *args):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        txt = self.buf.get_text(start, end)
        col_str = cparser.split(txt)[1:]
        self.model.highlight(col_str)
        self.view.repaint()

    def change_color(self, *args):
        colordlg = gtk.ColorSelectionDialog("Select color")
        colorsel = colordlg.colorsel

        response = colordlg.run()

        if response == gtk.RESPONSE_OK:
            col = colorsel.get_current_color()
            colordlg.destroy()
            if not self.color_tags.get(str(col), None):
                self.color_tags[str(col)]=self.buf.create_tag(str(col), foreground_gdk=col)
            end = self.buf.get_end_iter()
            self.buf.insert_with_tags(end, str(col)+": ", self.color_tags[str(col)], self.bold_tag)


