import gtk
import re
import pango
import bz2

class TextView(gtk.TextView):
    def __init__(self, *args, **kw):
        gtk.TextView.__init__(self, *args, **kw)
        self.txt_buff = self.get_buffer()

    def clear(self):
        self.txt_buff.delete(self.txt_buff.get_start_iter(),
                             self.txt_buff.get_end_iter())

    def get_text(self):
        start = self.txt_buff.get_start_iter()
        end = self.txt_buff.get_end_iter()
        return self.txt_buff.get_text(start, end)

    def copy(self, *args):
        clipboard = gtk.clipboard_get("CLIPBOARD")
        clipboard.set_text(self.get_text())

    def write_from_iterable(self, text_iterable):
        self.clear()
        for text in text_iterable:
            self.txt_buff.insert_at_cursor(text)


class HighlightTextView(TextView):
    def __init__(self, *args, **kw):
        TextView.__init__(self, *args, **kw)
        self.tag_table = self.txt_buff.get_tag_table()

    def remove_all_tags(self):
        start = self.txt_buff.get_start_iter()
        end = self.txt_buff.get_end_iter()
        self.txt_buff.remove_all_tags(start, end)

    def highlight(self, styles):
        self.remove_all_tags()
        text = self.get_text().decode('utf-8')
        for pattern, style in styles:
            style_re = re.compile(pattern)
            for m in style_re.finditer(text):
                self.apply_style_to_text_range(m.start(), m.end(), style)
                

    def highlight(self, styles):
        self.remove_all_tags()
        text = self.get_text().decode('utf-8')
        for pattern, style in styles:
            style_re = re.compile(pattern)
            for m in style_re.finditer(text):
                self.apply_style_to_text_range(m.start(), m.end(), style)
                

    def apply_style_to_text_range(self, start, end, style):
        start_iter = self.txt_buff.get_iter_at_offset(start)
        end_iter = self.txt_buff.get_iter_at_offset(end)
        self.txt_buff.remove_all_tags(start_iter, end_iter)
        for tag in style:
            ntag = self.tag_table.lookup(tag)
            if not ntag:
                ntag = self.txt_buff.create_tag(tag)
                att = tag[0]
                if att == "f":
                    ntag.set_property("foreground", tag[1:])
                elif att == "b":
                    if len(tag) > 1:
                        ntag.set_property("background", tag[1:])
                    else:
                        ntag.set_property("weight", pango.WEIGHT_BOLD)
                elif att.isdigit():
                    ntag.set_property("size", (int(tag)*
                                              pango.SCALE))
                elif att == "i":
                    ntag.set_property("style", pango.STYLE_ITALIC)
            self.txt_buff.apply_tag(ntag, start_iter, end_iter)

class SearchTextView(TextView):
    def __init__(self, *args, **kw):
        TextView.__init__(self, *args, **kw)
        self.selection_tag = self.txt_buff.create_tag("select")
        self.selection_tag.set_property("size", 13 * pango.SCALE)
        self.selection_tag.set_property("weight", pango.WEIGHT_BOLD)
        self.selection_tag.set_property("background", '#009')
        self.selection_tag.set_property("foreground", '#FFF')
        self.s = 0
        self.e = 0
        self.text_to_search = ""
        #self.p_cursor = gtk.gdk.Cursor(gtk.gdk.HAND1)
        #self.log_text.add_events(gtk.gdk.MOTION_NOTIFY | gtk.gdk.BUTTON_PRESS)
        #self.log_text.connect("motion_notify_event", self.motion_notify)
        #self.log_text.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        #self.log_text.connect("button-press-event", self.show_body)


    def select_string(self, s_pos, e_pos):
        s_iter = self.txt_buff.get_iter_at_offset(s_pos)
        e_iter = self.txt_buff.get_iter_at_offset(e_pos)
        self.scroll_to_iter(s_iter, 0)
        self.remove_selection()
        #self.txt_buff.select_range(s_iter, e_iter)
        self.txt_buff.apply_tag(self.selection_tag, s_iter, e_iter)
        self.s = e_pos
        self.e = s_pos
        self.not_found_var = -1

    def remove_selection(self):
        self.txt_buff.remove_tag(self.selection_tag,
            self.txt_buff.get_start_iter(),
            self.txt_buff.get_end_iter())

    def search(self, start_pos, f):
        s_pos, e_pos = f(start_pos)
        if e_pos:
            if s_pos > -1:
                self.select_string(s_pos, e_pos)
        else:
            self.txt_buff.remove_tag(self.selection_tag,
                self.txt_buff.get_start_iter(),
                self.txt_buff.get_end_iter())
            #self.txt_buff.select_range(self.txt_buff.get_end_iter(),
                                       #self.txt_buff.get_end_iter())

    def b_search(self, start_pos):
        text = self.get_text().decode('utf8').lower()[::-1]
        string_to_search = self.text_to_search.decode('utf8').lower()[::-1]  #!!
        chars = len(string_to_search)
        ltext = len(text)
        if chars > 0:
            tf = text.find(string_to_search, ltext - start_pos)
            if tf >= 0:
                pos = ltext - tf
                return (pos - chars, pos)
            else:
                return (self.not_found_var, self.not_found_var)
        else:
            return (None, None)

    def f_search(self, start_pos):
        text = self.get_text().decode('utf-8').lower()
        string_to_search = self.text_to_search.decode('utf8').lower() #!!
        chars = len(string_to_search)
        if chars > 0:
            pos = text.find(string_to_search, start_pos)
            if pos >= 0:
                return (pos, pos + chars)
            else:
                return (self.not_found_var,  self.not_found_var)
        else:
            return (None, None)

    def f_re_search(self, start_pos):
        text = self.get_text().decode('utf8')
        string_to_search = self.text_to_search.decode('utf8')
        if string_to_search:
            try:
                re_string = re.compile(string_to_search)
            except re.error:
                return (-1,-1)
            searched = re_string.search(text[start_pos:])
            if searched:
                s_pos = searched.start() + start_pos
                e_pos = searched.end() + start_pos
                return (s_pos, e_pos)
            else:
                return (self.not_found_var, self.not_found_var)
        else:
            return (None, None)

    def b_re_search(self, start_pos):
        text = self.get_text().decode('utf8')
        string_to_search = self.text_to_search.decode('utf8')
        if string_to_search:
            try:
                re_string = re.compile(string_to_search)
            except re.error:
                return (-1,-1)
            searched = list(re_string.finditer(text[:start_pos]))
            if searched:
                s_pos = searched[-1].start()
                e_pos = searched[-1].end()
                return (s_pos, e_pos)
            else:
                return (self.not_found_var, self.not_found_var)
        else:
            return (None, None)

    def reset_pos(self):
        self.s = 0
        self.e = 0

    def re_toggled_search(self, toggle):
        self.not_found_var = None
        self.remove_selection()
        self.reset_pos()
        self.re_search = toggle.get_active()
        self._next_search()

    def changed_search(self, entry, re_active):
        self.not_found_var = None
        self.reset_pos()
        self.text_to_search = entry.get_text()
        self.re_search = re_active()
        self._next_search()

    def prev_search(self, *args):
        self.not_found_var = -1
        self._prev_search()

    def next_search(self, *args):
        self.not_found_var = -1
        self._next_search()
        
    def _prev_search(self):
        if not self.re_search:
            self.search(self.e, self.b_search)
        else:
            self.search(self.e, self.b_re_search)

    def _next_search(self):
        if not self.re_search:
            self.search(self.s, self.f_search)
        else:
            self.search(self.s, self.f_re_search)


class PluginTextView(TextView):
    def __init__(self):
        TextView.__init__(self)
        self.text = ""

    def transform(self, transformation):
        text = self.get_text()
        self.txt_buff.set_text(transformation(text))
        self.text = bz2.compress(text)

    def restore(self):
        self.txt_buff.set_text(bz2.decompress(self.text))


class SearchHighlightTextView(SearchTextView, HighlightTextView, PluginTextView):
    def __init__(self, *args, **kw):
        SearchTextView.__init__(self, *args, **kw)
        HighlightTextView.__init__(self, *args, **kw)
        PluginTextView.__init__(self, *args, **kw)

    #pass
    #def show_body(self, widget, event, *args):
    #    if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
    #        iter_ = self.log_text.get_iter_at_location(int(event.x),
    #                                                   int(event.y))
    #        for s, e in self.procs:
    #            if s.get_offset() <= iter_.get_offset() <= e.get_offset():
    #                proc = self.txt_buff.get_text(s, e)
    #                PLSQL_Analyzer(proc)
    #                break

    #def motion_notify(self, widget, event):
    #    iter_ = self.log_text.get_iter_at_location(int(event.x), int(event.y))
    #    child_win = self.log_text.get_window(gtk.TEXT_WINDOW_TEXT)
    #    in_f = False
    #    for s, e in self.procs:
    #        if s.get_offset() <= iter_.get_offset() <= e.get_offset():
    #            in_f = True
    #    if in_f:
    #        child_win.set_cursor(self.p_cursor)
    #    else:
    #        child_win.set_cursor(None)

    #def motion_text(self, txt):
    #    m_iters = []
    #    procs = plsql_re.finditer(txt)
    #    for m in procs:
    #        start_iter = self.txt_buff.get_iter_at_offset(m.start())
    #        end_iter = self.txt_buff.get_iter_at_offset(m.end())
    #        m_iters.append((start_iter, end_iter))
    #    return m_iters



if __name__ == "__main__":
# Highlight
    wh = gtk.Window()
    wh.connect('destroy', lambda *a: gtk.main_quit())
    th = HighlightTextView()
    th.write_from_iterable(["testline1\n", "testline2\n", "testline3\n"])
    th.highlight([['\d+', ["f#f00", "b#ff0", "b", "i", "14"]],
                 ['line', ["i"]],
                 ['test', ['b']]])
    wh.add(th)
    wh.show_all()
#Search
    ws = gtk.Window()
    ws.connect('destroy', lambda *a: gtk.main_quit())
    ts = SearchTextView()
    hbox = gtk.HBox()
    r = gtk.CheckButton('r')
    r.connect('toggled', ts.re_toggled_search)
    pb = gtk.Button('<')
    pb.connect("clicked", ts.prev_search)
    nb = gtk.Button('>')
    nb.connect("clicked", ts.next_search)
    hbox.pack_start(r)
    box = gtk.VBox()
    e = gtk.Entry()
    hbox.pack_start(e)
    e.connect("changed", ts.changed_search, r.get_active)
    hbox.pack_start(pb)
    hbox.pack_start(nb)
    box.pack_start(hbox)
    box.pack_start(ts)
    ws.add(box)
    ws.show_all()
#Search and Highlight
    wsh = gtk.Window()
    wsh.connect('destroy', lambda *a: gtk.main_quit())
    tsh = SearchHighlightTextView()
    tsh.write_from_iterable(["testline1\n", "testline2\n", "testline3\n"])
    tsh.highlight([['\d+', ["f#f00", "b#ff0", "b", "i", "14"]],
                 ['line', ["i"]],
                 ['test', ['b']]])
    hbox = gtk.HBox()
    r = gtk.CheckButton('r')
    r.connect_after('toggled', tsh.re_toggled_search)
    pb = gtk.Button('<')
    pb.connect("clicked", tsh.prev_search)
    nb = gtk.Button('>')
    nb.connect("clicked", tsh.next_search)
    hbox.pack_start(r)
    box = gtk.VBox()
    e = gtk.Entry()
    hbox.pack_start(e)
    e.connect("changed", tsh.changed_search, r.get_active)
    hbox.pack_start(pb)
    hbox.pack_start(nb)
    box.pack_start(hbox)
    box.pack_start(tsh)
    wsh.add(box)
    wsh.show_all()
#Search and Highlight
    gtk.main()
