import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import os
import re
import pango

comment_line = re.compile("#.*")
section = re.compile("\[.+?\]")


class ConfigEditor:
    def __init__(self, config_path):
        self.config = config_path
        self.editor = gtk.Window()
        self.editor.set_title("%s editor" % os.path.basename(config_path))
        self.editor.set_default_size(640, 480)

        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.box = gtk.VBox()
        self.text = gtk.TextView()
        self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.scr.add(self.text)
        self.buf = self.text.get_buffer()
        self.buf.connect_after("insert-text", self.insert)
        self.text.connect_after("backspace", self.insert)
        self.comment_tag = self.buf.create_tag("comment", foreground="#ccc")
        self.section = self.buf.create_tag("bold", weight=pango.WEIGHT_BOLD)

        self.edited = False
        self.load_file()
        self.hl_comments()
        self.editor.set_title("%s editor" % os.path.basename(config_path))
        self.edited = False

        toolbar = gtk.Toolbar()

        toolbar.set_style(gtk.TOOLBAR_ICONS)
        savetb = gtk.ToolButton(gtk.STOCK_SAVE)
        savetb.connect("clicked", self.save)
        savetb.set_is_important(True)
        savetb.set_label("Save")
        cimage = gtk.Image()
        cimage.set_from_stock(gtk.STOCK_INDENT, gtk.ICON_SIZE_LARGE_TOOLBAR)
        cimage.show()
        commenttb = gtk.ToolButton()
        commenttb.connect("clicked", self.comment_lines)
        commenttb.set_is_important(True)
        commenttb.set_icon_widget(cimage)
        commenttb.set_label("Comment")
        uncimage = gtk.Image()
        uncimage.set_from_stock(gtk.STOCK_UNINDENT,
                                gtk.ICON_SIZE_LARGE_TOOLBAR)
        uncimage.show()
        uncommenttb = gtk.ToolButton()
        uncommenttb.connect("clicked", self.uncomment_lines)
        uncommenttb.set_is_important(True)
        uncommenttb.set_icon_widget(uncimage)
        uncommenttb.set_label("Uncomment")
        quittb = gtk.ToolButton(gtk.STOCK_QUIT)
        quittb.connect("clicked", self.quit)
        quittb.set_is_important(True)
        quittb.set_label("Quit")
        sep1 = gtk.SeparatorToolItem()
        sep2 = gtk.SeparatorToolItem()

        toolbar.insert(savetb, 0)
        toolbar.insert(sep1, 1)
        toolbar.insert(commenttb, 2)
        toolbar.insert(uncommenttb, 3)
        toolbar.insert(sep2, 4)
        toolbar.insert(quittb, 5)
        toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)

        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.scr)

        self.editor.add(self.box)
        self.editor.show_all()

    def get_text(self):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        return self.buf.get_text(start, end)

    def save(self, *args):
        text = self.get_text()
        f = open(self.config, "w")
        f.write(text)
        f.close()
        self.edited = False
        title = self.editor.get_title()
        self.editor.set_title(title[1:])

    def quit(self, *args):
        self.editor.destroy()

    def comment_lines(self, *args):
        sel = self.buf.get_selection_bounds()
        if sel:
            start_line = sel[0].get_line()
            end_line = sel[1].get_line()
            line = start_line
            while line != end_line + 1:
                iter = self.buf.get_iter_at_line(line)
                if iter.get_char() != "#":
                    self.buf.insert(iter, "#")
                line += 1
        else:
            pos = self.get_iter_position()
            line = pos.get_line()
            start_iter = self.buf.get_iter_at_line(line)
            if start_iter.get_char() != "#":
                self.buf.insert(start_iter, "#")

    def uncomment_lines(self, *args):
        sel = self.buf.get_selection_bounds()
        if sel:
            start_line = sel[0].get_line()
            end_line = sel[1].get_line()
            line = start_line
            while line != end_line + 1:
                iter = self.buf.get_iter_at_line(line)
                if iter.get_char() == "#":
                    end_iter = self.buf.get_iter_at_line_offset(line, 1)
                    self.buf.delete(iter, end_iter)
                line += 1
        else:
            pos = self.get_iter_position()
            line = pos.get_line()
            start_iter = self.buf.get_iter_at_line(line)
            if start_iter.get_char() == "#":
                end_iter = self.buf.get_iter_at_line_offset(line, 1)
                self.buf.delete(start_iter, end_iter)
        self.hl_comments()

    def get_iter_position(self):
        return self.buf.get_iter_at_mark(self.buf.get_insert())

    def load_file(self):
        with open(self.config) as f:
            self.first_text = f.read()
        self.buf.set_text(self.first_text)

    def insert(self, *args):
        if not self.edited:
            title = self.editor.get_title()
            self.editor.set_title("*" + title)
            self.edited = True
        self.hl_comments()

    def hl_comments(self):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        self.buf.remove_all_tags(start, end)
        text = self.buf.get_text(start, end)
        for m in section.finditer(text.decode('utf8')):
            start_iter = self.buf.get_iter_at_offset(m.start())
            end_iter = self.buf.get_iter_at_offset(m.end())
            self.buf.apply_tag(self.section, start_iter, end_iter)
        for m in comment_line.finditer(text.decode('utf8')):
            start_iter = self.buf.get_iter_at_offset(m.start())
            end_iter = self.buf.get_iter_at_offset(m.end())
            self.buf.apply_tag(self.comment_tag, start_iter, end_iter)
