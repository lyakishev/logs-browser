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
        self.filter = self.model.get_model().filter_new()
        self.filter.set_visible_column(7)


        self.text = gtk.TextView()
        self.text.set_wrap_mode(gtk.WRAP_CHAR)
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
        self.buf.connect_after("insert-text", self.tags_text)
        self.text.connect("backspace", self.backspace)

        self.buf.create_tag('#f00', foreground='#f00')
        self.buf.create_tag('#0f0', foreground='#0f0')
        self.buf.create_tag('#00f', foreground='#00f')
        self.buf.create_tag('#dd0', foreground='#dd0')
        self.bold_tag = self.buf.create_tag("bold", weight=pango.WEIGHT_BOLD)
        self.white_tag = self.buf.create_tag("#fff", foreground="#000")

        self.start_col = 0
        self.in_color = 0
        self.colon = 0

        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#f00:", '#f00', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#0f0:", '#0f0', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#00f:", '#00f', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#dd0:", '#dd0', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')


    def backspace(self, *args):
        self.start_col -= 1

    def get_iter_position(self):
        return self.buf.get_iter_at_mark(self.buf.get_insert())


    def tags_text(self, buf, textiter, text, length):
        if text == "#":
            self.start_col = 1
            self.colon = 0
        elif text == ":":
            if not self.colon:
                iter_start = self.get_iter_position()
                iter_start.backward_chars(self.start_col+1)
                iter_end = self.get_iter_position()
                iter_end.backward_char()
                colname = self.buf.get_text(iter_start, iter_end)
                try:
                    color = gtk.gdk.Color(colname)
                except ValueError:
                    print colname
                    self.buf.backspace(self.get_iter_position(), False, True)
                    return
                self.start_col+=1
                ttable = self.buf.get_tag_table()
                tag = ttable.lookup(colname)
                tag = tag if tag else self.buf.create_tag(colname, foreground=colname)
                self.buf.apply_tag(tag, iter_start, self.get_iter_position())
                self.buf.apply_tag(self.bold_tag, iter_start, self.get_iter_position())
                self.colon = 1
        else:
            self.start_col += length

    def filter_logs(self, *args):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        txt = self.buf.get_text(start, end)
        col_str = cparser.split(txt)[1:]
        self.model.highlight(col_str)
        if self.hide_other.get_active():
            self.view.view.set_model(self.filter)
        else:
            self.view.view.set_model(self.model.get_model())
        self.view.repaint()

    def change_color(self, *args):
        colordlg = gtk.ColorSelectionDialog("Select color")
        colorsel = colordlg.colorsel

        response = colordlg.run()

        if response == gtk.RESPONSE_OK:
            col = colorsel.get_current_color()
            colordlg.destroy()
            ttable = self.buf.get_tag_table()
            tag = ttable.lookup(str(col))
            tag = tag if tag else self.buf.create_tag(str(col), foreground_gdk=col)
            end = self.buf.get_end_iter()
            self.buf.insert_with_tags(end, str(col)+": ", tag, self.bold_tag)


