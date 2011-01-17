import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import re
import pango
from itertools import permutations

cparser = re.compile(r"(#[a-fA-F0-9]{3,}):", re.U)

bg = "(?P<bg>b#[A-Fa-f0-9]{3,})"
fg = "(?P<fg>f#[A-Fa-f0-9]{3,})"
fstyle = "s#(?P<size>\d{,2})(?P<style>(bi|ib|b|i))?"
prmttns = list(permutations([bg,fg,fstyle], 3))+list(permutations([bg,fg,fstyle], 2))+list(permutations([bg,fg,fstyle], 1))
style_re = "("+"|".join([("("+",".join(e)+")").replace("bg", "bg%d"%n).replace("fg", "fg%d"%n).replace("size", "size%d"%n).replace("style", "style%d"%n) for n,e in enumerate(prmttns)])+"):"
style = re.compile(style_re, re.U)

class ColorParser(gtk.HBox):
    def __init__(self, model, view):
        super(ColorParser, self).__init__()

        self.model = model
        self.view = view
        self.filter = self.model.get_model().filter_new()
        self.filter.set_visible_column(7)


        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
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

        self.scroll.add(self.text)
        self.pack_start(self.scroll, True, True, 2)
        self.pack_start(self.button_box, False, False)

        self.filter_button.connect("clicked", self.filter_logs)
        self.color_button.connect("clicked", self.change_color)
        self.buf.connect_after("insert-text", self.tags_text)
        self.text.connect_after("backspace", self.backspace)

        self.buf.create_tag('#f00', foreground='#f00')
        self.buf.create_tag('#0f0', foreground='#0f0')
        self.buf.create_tag('#00f', foreground='#00f')
        self.buf.create_tag('#dd0', foreground='#dd0')
        self.bold_tag = self.buf.create_tag("bold", weight=pango.WEIGHT_BOLD)
        self.white_tag = self.buf.create_tag("#fff", foreground="#000", style=pango.STYLE_ITALIC)
        self.error_tag = self.buf.create_tag("error", style=pango.STYLE_ITALIC, foreground="#f00")

        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#f00:", '#f00', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#0f0:", '#0f0', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#00f:", '#00f', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#dd0:", '#dd0', 'bold')
        self.buf.insert(self.buf.get_end_iter(), '  ')
        self.buf.insert_with_tags_by_name(self.buf.get_end_iter(), "#fff:", '#fff', 'bold')
        self.buf.insert(self.buf.get_end_iter(), ' ')

        self.tags_ranges = []
        self.parse_and_highlight()


    def get_iter_position(self):
        return self.buf.get_iter_at_mark(self.buf.get_insert())

    def parse_and_highlight(self):
        self.tags_ranges = []
        ttable = self.buf.get_tag_table()
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        self.buf.remove_all_tags(start, end)
        txt = self.buf.get_text(start, end)
        for m in cparser.finditer(txt):
            start = m.start()
            end = m.end()
            self.tags_ranges.append([start,end])
            start_iter = self.buf.get_iter_at_offset(start)
            end_iter = self.buf.get_iter_at_offset(end)
            col = m.group()[:-1]
            tag = ttable.lookup(col)
            tag = tag if tag else self.buf.create_tag(col, foreground=col)
            self.buf.apply_tag(tag, start_iter, end_iter)
            self.buf.apply_tag(self.bold_tag, start_iter, end_iter)

    def t_range(self, offset):
        for start, end in self.tags_ranges:
            if start<offset<end:
                return [start, end]
        return None

    def backspace(self, *args):
        self.parse_and_highlight()

    def tags_text(self, buf, textiter, text, length):
        if text == "\t":
            self.buf.backspace(self.get_iter_position(), False, True)
            place = self.get_iter_position().get_offset()
            try:
                new_place = min([i[1] for i in self.tags_ranges if place<i[1]])+1
            except ValueError:
                new_place = self.tags_ranges[0][1]+1
            new_iter_place = self.buf.get_iter_at_offset(new_place)
            self.buf.place_cursor(new_iter_place)
        self.parse_and_highlight()

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
        offset = self.get_iter_position().get_offset()
        in_col = self.t_range(offset)
        colordlg = gtk.ColorSelectionDialog("Select color")
        colorsel = colordlg.colorsel
        colorsel.set_has_palette(True)

        response = colordlg.run()

        if response == gtk.RESPONSE_OK:
            col = colorsel.get_current_color()
            colordlg.destroy()
            if in_col:
                col_start = self.buf.get_iter_at_offset(in_col[0])
                col_end = self.buf.get_iter_at_offset(in_col[1])
                self.buf.delete(col_start, col_end)
                self.buf.insert(col_start, str(col)+": ")
                new_end = self.buf.get_iter_at_offset(in_col[0]+len(str(col)+": "))
                self.buf.place_cursor(new_end)
            else:
                end = self.buf.get_end_iter()
                self.buf.insert(end, str(col)+": ")
                self.buf.place_cursor(self.buf.get_end_iter())
            self.text.grab_focus()
        else:
            colordlg.destroy()


class LogColorParser(gtk.HBox):
    def __init__(self, logw):
        super(LogColorParser, self).__init__()

        self.logw = logw
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.text = gtk.TextView()
        self.text.set_wrap_mode(gtk.WRAP_CHAR)
        self.buf = self.text.get_buffer()
        self.filter_button = gtk.Button("Filter")
        self.color_button = gtk.Button("Color")

        self.button_box = gtk.VButtonBox()
        self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.button_box.pack_start(self.filter_button)
        self.button_box.pack_start(self.color_button)

        self.scroll.add(self.text)
        self.pack_start(self.scroll, True, True, 2)
        self.pack_start(self.button_box, False, False)

        self.filter_button.connect("clicked", self.filter_logs)
        self.color_button.connect("clicked", self.change_color)
        self.buf.connect_after("insert-text", self.tags_text)
        self.text.connect_after("backspace", self.backspace)

        self.bold = self.buf.create_tag("bold", weight=pango.WEIGHT_BOLD)
        self.italic = self.buf.create_tag("italic", style=pango.STYLE_ITALIC)
        self.parse_and_highlight()

    def parse_and_highlight(self):
        self.tags_ranges = {}
        self.col_str = {}
        ttable = self.buf.get_tag_table()
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        self.buf.remove_all_tags(start, end)
        txt = self.buf.get_text(start, end)
        for m in style.finditer(txt):
            start = m.start()
            end = m.end()
            trange = (start, end)
            self.col_str[trange] = []
            start_iter = self.buf.get_iter_at_offset(start)
            end_iter = self.buf.get_iter_at_offset(end)
            style_dict = m.groupdict()
            for k, v in style_dict.iteritems():
                if v:
                    if "bg" in k:
                        bgcol = style_dict[k][1:]
                        tag = ttable.lookup(style_dict[k])
                        tag = tag if tag else self.buf.create_tag(style_dict[k], background=bgcol)
                        self.buf.apply_tag(tag, start_iter, end_iter)
                        bgfgranges = self.tags_ranges.get(trange, {})
                        bgfgranges["b"] = (m.start(k),m.end(k))
                        self.tags_ranges[trange]=bgfgranges
                        self.col_str[trange].append(style_dict[k])
                    elif "fg" in k:
                        fgcol = style_dict[k][1:]
                        tag = ttable.lookup(style_dict[k])
                        tag = tag if tag else self.buf.create_tag(style_dict[k], foreground=fgcol)
                        self.buf.apply_tag(tag, start_iter, end_iter)
                        bgfgranges = self.tags_ranges.get(trange, {})
                        bgfgranges["f"] = (m.start(k),m.end(k))
                        self.tags_ranges[trange]=bgfgranges
                        self.col_str[trange].append(style_dict[k])
                    elif "style" in k:
                        weight = style_dict[k]
                        for w in weight:
                            if w == "i":
                                self.buf.apply_tag(self.italic, start_iter, end_iter)
                                self.col_str[trange].append("i")
                            if w == "b":
                                self.buf.apply_tag(self.bold, start_iter, end_iter)
                                self.col_str[trange].append("b")
                    elif "size" in k:
                        size = style_dict[k]
                        tag = ttable.lookup("s"+size)
                        tag = tag if tag else self.buf.create_tag("s"+size, size=int(size)*pango.SCALE)
                        self.buf.apply_tag(tag, start_iter, end_iter)
                        self.col_str[trange].append("s"+size)

    def tags_text(self, *args):
        self.parse_and_highlight()

    def backspace(self, *args):
        self.parse_and_highlight()

    def t_range(self, offset):
        for full_range, part in self.tags_ranges.iteritems():
            if full_range[0]<offset<full_range[1]:
                for st, part_range in part.iteritems():
                    if part_range[0]<offset<part_range[1]:
                        return [st, part_range[0], part_range[1]]
        return None

    def get_iter_position(self):
        return self.buf.get_iter_at_mark(self.buf.get_insert())
        

    def change_color(self, *args):
        offset = self.get_iter_position().get_offset()
        in_col = self.t_range(offset)
        colordlg = gtk.ColorSelectionDialog("Select color")
        colorsel = colordlg.colorsel
        colorsel.set_has_palette(True)

        response = colordlg.run()

        if response == gtk.RESPONSE_OK:
            col = colorsel.get_current_color()
            colordlg.destroy()
            if in_col:
                col_start = self.buf.get_iter_at_offset(in_col[1])
                col_end = self.buf.get_iter_at_offset(in_col[2])
                self.buf.delete(col_start, col_end)
                self.buf.insert(col_start, in_col[0]+str(col))
                new_end = self.buf.get_iter_at_offset(in_col[1]+len(in_col[0]+str(col)))
                self.buf.place_cursor(new_end)
            else:
                end = self.buf.get_end_iter()
                self.buf.insert(end, str(col)+": ")
                self.buf.place_cursor(self.buf.get_end_iter())
            self.text.grab_focus()
        else:
           colordlg.destroy()

    def def_text_ranges(self):
        text_range = {}
        pat_list=[]
        prev_start = 0
        skeys = sorted(self.col_str.keys(), key=lambda x: x[0])
        for tag_range in skeys:
            tags = self.col_str[tag_range]
            end = tag_range[0]
            if prev_start:
                tstart = self.buf.get_iter_at_offset(prev_start)
                tend = self.buf.get_iter_at_offset(end)
                exp = self.buf.get_text(tstart, tend).strip()
                text_range[exp] = tgs
                pat_list.append(exp)
            prev_start = tag_range[1]
            tgs = tags
        if prev_start:
            tstart = self.buf.get_iter_at_offset(prev_start)
            tend = self.buf.get_end_iter()
            exp=self.buf.get_text(tstart, tend).strip()
            text_range[exp] = tgs
            pat_list.append(exp)
        return (text_range, pat_list)
            

    def filter_logs(self, *args):
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        txt = self.buf.get_text(start, end)
        col_str = self.def_text_ranges()
        self.logw.highlight(col_str)



        



