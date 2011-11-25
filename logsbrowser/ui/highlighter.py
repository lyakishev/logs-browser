# LogsBrowser is program for find and analyze logs.
# Copyright (C) <2010-2011>  <Lyakishev Andrey (lyakav@gmail.com)>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import re
import pango
from itertools import permutations
from textview import HighlightTextView
from button import Button
from toolbar import Toolbar

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

COLOR_RE = re.compile("%s|%s" % (FOREGROUND, BACKGROUND))

STYLE = re.compile(STYLE_RE)
digits = re.compile('\d+')


class HighlightSyntaxTextView(HighlightTextView):
    def __init__(self):
        HighlightTextView.__init__(self)
        self.txt_buff.connect_after("insert-text", lambda *a: self.highlight())
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.change_color)
        self.connect_after("backspace", lambda *a: self.highlight())
        self.tags_ranges = []

    def get_iter_position(self):
        return self.txt_buff.get_iter_at_mark(self.txt_buff.get_insert())

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

    def get_splitted_text(self):
        text = self.get_text()
        return STYLE.split(text)[1:]

    def get_style(self):
        style = []
        text_to_style = self.get_splitted_text()
        for _style in text_to_style[:-1:2]:
            style.append((_style, self.parse_style(_style)))
        return style

    def get_syntax(self):
        style = []
        text_to_style = self.get_splitted_text()
        for _style, pattern in zip(text_to_style[0::2], text_to_style[1::2]):
            style.append((pattern.strip(), self.parse_style(_style)))
        return style

    def pos_in_color(self, pos):
        text = self.get_text()
        for m in COLOR_RE.finditer(text):
            start = m.start()
            end = m.end()
            if start <= pos <= end:
                return (start+1, end)

    def change_color(self, widget, event, *args):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.set_property('editable', False)
            offset = self.get_iter_position().get_offset()
            in_col = self.pos_in_color(offset)
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
                    self.txt_buff.insert(col_start, str(col))
                    new_end = self.txt_buff.get_iter_at_offset(in_col[0] +\
                                                          len(str(col)))
                    self.txt_buff.place_cursor(new_end)
                else:
                    end = self.txt_buff.get_end_iter()
                    self.txt_buff.insert(end, " f%s: " % str(col))
                    self.txt_buff.place_cursor(self.txt_buff.get_end_iter())
                self.grab_focus()
            else:
                colordlg.destroy()
            self.set_property('editable', True)
            end = self.txt_buff.get_end_iter()
            return True


class Highlighter(gtk.HBox):
    def __init__(self, apply_act, save_act, save_as_act):
        gtk.HBox.__init__(self)
        self.textview = HighlightSyntaxTextView()
        scr = gtk.ScrolledWindow()
        scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scr.add(self.textview)
        toolbar = Toolbar()
        apply_btn = toolbar.append_button(gtk.STOCK_APPLY, apply_act)
        save_btn = toolbar.append_button(gtk.STOCK_SAVE, save_act)
        save_as_btn = toolbar.append_button(gtk.STOCK_SAVE_AS, save_as_act)
        toolbar.set_orientation(gtk.ORIENTATION_VERTICAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.pack_start(scr, True, True)
        self.pack_start(toolbar, False, False)

    def __getattr__(self, name):
        return getattr(self.textview, name)


if __name__ == "__main__":
    wh = gtk.Window()
    wh.connect('destroy', lambda *a: gtk.main_quit())
    box = gtk.VBox()
    th = HighlightTextView()
    box.pack_start(th, True, True, 4)
    hbox = gtk.HBox()
    button = gtk.Button('=')
    thh = HighlightSyntaxTextView()
    hbox.pack_start(thh, True, True, 4)
    hbox.pack_start(button)
    box.pack_start(hbox)
    button.connect('clicked', lambda *a: th.highlight(thh.get_syntax()))
    wh.add(box)
    wh.show_all()
    gtk.main()

