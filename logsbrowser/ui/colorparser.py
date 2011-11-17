import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import re
import pango
from itertools import permutations
from textview import HighlightTextView

BACKGROUND = "(?:b#[A-Fa-f0-9]{3,})"
FOREGROUND = "(?:f#[A-Fa-f0-9]{3,})"
FONT_STYLE = "(?:s#\d{,2}(?:bi|ib|b|i)?)"
STYLE_VARIANTS = list(permutations([BACKGROUND, FOREGROUND, FONT_STYLE], 3)) +\
          list(permutations([BACKGROUND, FOREGROUND, FONT_STYLE], 2)) +\
          list(permutations([BACKGROUND, FOREGROUND, FONT_STYLE], 1))
STYLE_RE = "(" +\
           "|".join(\
                [("(?:" + ",".join(e) + ")")
                for n, e in enumerate(STYLE_VARIANTS)]) +\
            "):"
STYLE = re.compile(STYLE_RE)
digits = re.compile('\d+')


class HighlightSyntaxTextView(HighlightTextView):
    def __init__(self):
        HighlightTextView.__init__(self)
        self.txt_buff.connect_after("insert-text", self.tags_text)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.change_color)
        self.connect_after("backspace", lambda *a: self.highlight())
        self.tags_ranges = []

    def get_iter_position(self):
        return self.txt_buff.get_iter_at_mark(self.txt_buff.get_insert())

    def pos_is_highlighted(self, offset):
        for start, end in self.tags_ranges:
            if start < offset < end:
                return [start, end]
        return None

    def tags_text(self, buf, textiter, text, length):
        if text == "\t":
            buf.backspace(self.get_iter_position(), False, True)
            place = self.get_iter_position().get_offset()
            try:
                new_place = min([i[1] for i in self.tags_ranges
                                if place < i[1]]) + 1
            except ValueError:
                new_place = self.tags_ranges[0][1] + 1
            new_iter_place = buf.get_iter_at_offset(new_place)
            buf.place_cursor(new_iter_place)
        self.highlight()

    def highlight(self):
        HighlightTextView.highlight(self, self.get_style())

    def parse_style(self, style):
        parsed_styles = []
        for style_ in style.split(','):
            if style_.startswith('f#'):
                parsed_styles.append(style_)
            elif style_.startswith('b#'):
                parsed_styles.append(style_)
            elif style_.startswith('s#'):
                pos = 0
                if 'b' in style_:
                    parsed_styles.append('b')
                    pos += 1
                if 'i' in style_:
                    parsed_styles.append('i')
                    pos += 1
                size = style_[2: -pos or None]
                if size and size.isdigit():
                    parsed_styles.append(size)
        return parsed_styles

    def get_style(self):
        text = self.get_text()
        style = []
        text_to_style = STYLE.split(text)[1:]
        for _style in text_to_style[:-1:2]:
            style.append((_style, self.parse_style(_style)))
        return style

    def change_color(self, widget, event, *args):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.set_property('editable', False)
            offset = self.get_iter_position().get_offset()
            in_col = self.pos_is_highlighted(offset)
            colordlg = gtk.ColorSelectionDialog("Select color")
            colorsel = colordlg.colorsel
            colorsel.set_has_palette(True)

            response = colordlg.run()

            if response == gtk.RESPONSE_OK:
                col = colorsel.get_current_color()
                colordlg.destroy()
                if in_col:
                    col_start = self.txt_buff.get_iter_at_offset(in_col[0])
                    col_end = self.txt_buff.get_iter_at_offset(in_col[1])
                    self.txt_buff.delete(col_start, col_end)
                    self.txt_buff.insert(col_start, str(col) + ": ")
                    new_end = self.txt_buff.get_iter_at_offset(in_col[0] +\
                                                          len(str(col)\
                                                          + ": "))
                    self.txt_buff.place_cursor(new_end)
                else:
                    end = self.txt_buff.get_end_iter()
                    self.txt_buff.insert(end, str(col) + ": ")
                    self.txt_buff.place_cursor(self.txt_buff.get_end_iter())
                self.text.grab_focus()
            else:
                colordlg.destroy()
            self.set_property('editable', True)


class LogColorParser(gtk.HBox):
    def __init__(self, logw):
        super(LogColorParser, self).__init__()

        self.logw = logw
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.text = gtk.TextView()
        self.text.set_wrap_mode(gtk.WRAP_CHAR)
        self.buf = self.text.get_buffer()
        filter_button = gtk.Button("Highlight")
        color_button = gtk.Button("Color")

        button_box = gtk.VButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        button_box.pack_start(filter_button)
        button_box.pack_start(color_button)

        scroll.add(self.text)
        self.pack_start(scroll, True, True, 2)
        self.pack_start(button_box, False, False)

        filter_button.connect("clicked", self.filter_logs)
        color_button.connect("clicked", self.change_color)
        self.buf.connect_after("insert-text", self.tags_text)
        self.text.connect_after("backspace", self.backspace)

        self.bold = self.buf.create_tag("bold", weight=pango.WEIGHT_BOLD)
        self.italic = self.buf.create_tag("italic", style=pango.STYLE_ITALIC)
        self.parse_and_highlight()

    def parse_and_highlight(self):
        def apply_tag(bg_fg):
            col = style_dict[key][1:]
            tag = ttable.lookup(style_dict[key])
            if not tag:
                if bg_fg == "bg":
                    tag = self.buf.create_tag(style_dict[key],
                                  background=col)
                elif bg_fg == "fg":
                    tag = self.buf.create_tag(style_dict[key],
                                  foreground=col)
            self.buf.apply_tag(tag, start_iter, end_iter)
            bgfgranges = self.tags_ranges.get(trange, {})
            bgfgranges[bg_fg[:1]] = (match.start(key), match.end(key))
            self.tags_ranges[trange] = bgfgranges
            self.col_str[trange].append(style_dict[key])
            
        self.tags_ranges = {}
        self.col_str = {}
        ttable = self.buf.get_tag_table()
        start = self.buf.get_start_iter()
        end = self.buf.get_end_iter()
        self.buf.remove_all_tags(start, end)
        txt = self.buf.get_text(start, end).decode('utf-8')
        for match in STYLE.finditer(txt):
            start = match.start()
            end = match.end()
            trange = (start, end)
            self.col_str[trange] = []
            start_iter = self.buf.get_iter_at_offset(start)
            end_iter = self.buf.get_iter_at_offset(end)
            style_dict = match.groupdict()
            for key, value in style_dict.iteritems():
                if value:
                    if "bg" in key:
                        apply_tag("bg")
                    elif "fg" in key:
                        apply_tag("fg")
                    elif "style" in key:
                        weight = style_dict[key]
                        for w in weight:
                            if w == "i":
                                self.buf.apply_tag(self.italic, start_iter,
                                                                end_iter)
                            if w == "b":
                                self.buf.apply_tag(self.bold, start_iter,
                                                              end_iter)
                            self.col_str[trange].append(w)
                    elif "size" in key:
                        size = "s" + style_dict[key]
                        tag = ttable.lookup(size) or\
                              self.buf.create_tag(size,
                                            size=int(size[1:]) * pango.SCALE)
                        self.buf.apply_tag(tag, start_iter, end_iter)
                        self.col_str[trange].append(size)

    #def tags_text(self, *args):
    #    self.parse_and_highlight()

    #def backspace(self, *args):
    #    self.parse_and_highlight()

    def t_range(self, offset):
        for full_range, part in self.tags_ranges.iteritems():
            if full_range[0] < offset < full_range[1]:
                for st, part_range in part.iteritems():
                    if part_range[0] < offset < part_range[1]:
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
                self.buf.insert(col_start, in_col[0] + str(col))
                new_end = self.buf.get_iter_at_offset(in_col[1] +\
                                                      len(in_col[0] +\
                                                      str(col)))
                self.buf.place_cursor(new_end)
            else:
                end = self.buf.get_end_iter()
                self.buf.insert(end, str(col) + ": ")
                self.buf.place_cursor(self.buf.get_end_iter())
            self.text.grab_focus()
        else:
            colordlg.destroy()

    def def_text_ranges(self):
        text_range = {}
        pat_list = []
        prev_start = 0
        skeys = sorted(self.col_str.keys(), key=lambda x: x[0])
        for tag_range in skeys:
            tags = self.col_str[tag_range]
            end = tag_range[0]
            if prev_start:
                tstart = self.buf.get_iter_at_offset(prev_start)
                tend = self.buf.get_iter_at_offset(end)
                exp = self.buf.get_text(tstart, tend).decode('utf-8').strip()
                text_range[exp] = tgs
                pat_list.append(exp)
            prev_start = tag_range[1]
            tgs = tags
        if prev_start:
            tstart = self.buf.get_iter_at_offset(prev_start)
            tend = self.buf.get_end_iter()
            exp = self.buf.get_text(tstart, tend).decode('utf-8').strip()
            text_range[exp] = tgs
            pat_list.append(exp)
        return (text_range, pat_list)

    def filter_logs(self, *args):
        col_str = self.def_text_ranges()
        self.logw.highlight(col_str)


if __name__ == "__main__":
    wh = gtk.Window()
    wh.connect('destroy', lambda *a: gtk.main_quit())
    th = HighlightSyntaxTextView()
    wh.add(th)
    wh.show_all()
    gtk.main()

