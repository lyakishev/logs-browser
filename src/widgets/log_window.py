# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio
import re
import xml.dom.minidom
import os
import threading
from widgets.color_parser import LogColorParser
import pango
import traceback
try:
    from plsql_analyzer import *
except:
    pass

#xml_re = re.compile("<\?xml(.+)>")
#xml_spl = re.compile(r"(<\?xml.+?>)")
#xml_s = re.compile(r"<\?xml.+?>", re.DOTALL)
#xml_s2 = re.compile(r"(?P<xml><.+>)(?P<other>.*)")
plsql_re = re.compile(r"(?<=\s|')(\w|_)+\.(\w|_)+(?=\s|')")


class LogWindow:
    def __init__(self, loglist, iter, sel):
        self.model = loglist.model
        self.view = loglist.view
        self.loglist = loglist
        self.selection = sel
        self.iter = iter
        self.popup = gtk.Window()
        self.popup.set_title("Log")
        self.popup.set_default_size(700, 700)
        self.box = gtk.VBox()
        self.open_info_box = gtk.VBox()
        self.info_box = gtk.HBox()
        self.info_label = gtk.Label()
        self.info_label.set_selectable(True)
        self.open_label = gtk.Label()
        self.open_label.set_selectable(True)
        self.info_box.pack_start(self.open_info_box)
        self.open_info_box.pack_start(self.info_label)
        self.open_info_box.pack_start(self.open_label)
        self.updown_btns = gtk.VButtonBox()
        self.up = gtk.Button()
        up_im = gtk.Image()
        up_im.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_BUTTON)
        self.up.add(up_im)
        self.up.connect("clicked", self.show_next)
        self.down = gtk.Button()
        dwn_im = gtk.Image()
        dwn_im.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_BUTTON)
        self.down.add(dwn_im)
        self.down.connect("clicked", self.show_prev)
        self.updown_btns.pack_start(self.up)
        self.updown_btns.pack_start(self.down)
        self.info_box.pack_start(self.updown_btns, False, False, padding=30)
        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.log_text = gtk.TextView()
        self.txt_buff = self.log_text.get_buffer()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_WORD)
        self.log_text.add_events(gtk.gdk.MOTION_NOTIFY | gtk.gdk.BUTTON_PRESS)
        self.log_text.connect("motion_notify_event", self.motion_notify)
        self.log_text.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.log_text.connect("button-press-event", self.show_body)
        self.scr.add(self.log_text)
        self.popup.add(self.box)

        toolbar = gtk.Toolbar()
        open_btn = gtk.ToolButton(gtk.STOCK_OPEN)
        open_btn.connect("clicked", self.open_file)
        save_btn = gtk.ToolButton(gtk.STOCK_SAVE)
        save_btn.connect("clicked", self.save_to_file)
        copy_btn = gtk.ToolButton(gtk.STOCK_COPY)
        copy_btn.connect("clicked", self.copy_log)
        sep1 = gtk.SeparatorToolItem()
        find_label = gtk.Label("Find:")
        find_label_item = gtk.ToolItem()
        find_label_item.add(find_label)
        self.find_entry = gtk.Entry()
        self.find_entry.connect("changed", self.insert_search)
        find_entry_item = gtk.ToolItem()
        find_entry_item.add(self.find_entry)
        prev_btn = gtk.ToolButton(gtk.STOCK_GO_BACK)
        prev_btn.connect("clicked", self.prev_search)
        next_btn = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        next_btn.connect("clicked", self.next_search)
        self.re_toggle = gtk.CheckButton("regexp")
        self.re_toggle.connect_after("toggled", self.t_insert_search)
        re_toggle_item = gtk.ToolItem()
        re_toggle_item.add(self.re_toggle)
        sep2 = gtk.SeparatorToolItem()
        hl_btn = gtk.ToggleToolButton(gtk.STOCK_SELECT_COLOR)
        hl_btn.connect("toggled", self.show_hl)
        self.syntax = gtk.combo_box_new_text()
        self.syntax.connect("changed", self.combo_hl)
        syntax_item = gtk.ToolItem()
        syntax_item.add(self.syntax)
        sims_btn = gtk.ToolButton(gtk.STOCK_FIND)
        sims_btn.connect("clicked", self.find_sims)

        toolbar.insert(open_btn, 0)
        toolbar.insert(save_btn, 1)
        toolbar.insert(copy_btn, 2)
        toolbar.insert(sep1, 3)
        toolbar.insert(find_label_item, 4)
        toolbar.insert(find_entry_item, 5)
        toolbar.insert(prev_btn, 6)
        toolbar.insert(next_btn, 7)
        toolbar.insert(re_toggle_item, 8)
        toolbar.insert(sep2, 9)
        toolbar.insert(syntax_item, 10)
        toolbar.insert(hl_btn, 11)
        toolbar.insert(sims_btn, 12)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)

        self.filter = LogColorParser(self)

        self.selection_tag = self.txt_buff.create_tag("select")
        self.selection_tag.set_property("size", 13 * pango.SCALE)
        self.selection_tag.set_property("weight", pango.WEIGHT_BOLD)
        self.selection_tag.set_property("background", '#009')
        self.selection_tag.set_property("foreground", '#FFF')

        self.paned = gtk.VBox()
        self.paned.pack_start(self.scr, True, True)
        self.paned.pack_start(self.filter, False, False, padding=5)

        self.box.pack_start(self.info_box, False, False, padding=10)
        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.paned)
        self.tag_table = self.txt_buff.get_tag_table()
        self.col_str = ({}, [])
        self.read_config()
        self.p_cursor = gtk.gdk.Cursor(gtk.gdk.HAND1)

        self.fill()
        self.fill_combo()

        self.popup.show_all()
        self.filter.hide()

    def find_sims(self, *args):
        self.loglist.find_similar(self.get_text())

    def show_body(self, widget, event, *args):
        if event.button == 1 and event.type == gtk.gdk.BUTTON_PRESS:
            iter_ = self.log_text.get_iter_at_location(int(event.x),
                                                       int(event.y))
            for s, e in self.procs:
                if s.get_offset() <= iter_.get_offset() <= e.get_offset():
                    proc = self.txt_buff.get_text(s, e)
                    PLSQL_Analyzer(proc)
                    break

    def motion_notify(self, widget, event):
        iter_ = self.log_text.get_iter_at_location(int(event.x), int(event.y))
        child_win = self.log_text.get_window(gtk.TEXT_WINDOW_TEXT)
        in_f = False
        for s, e in self.procs:
            if s.get_offset() <= iter_.get_offset() <= e.get_offset():
                in_f = True
        if in_f:
            child_win.set_cursor(self.p_cursor)
        else:
            child_win.set_cursor(None)

    def motion_text(self, txt):
        m_iters = []
        procs = plsql_re.finditer(txt)
        for m in procs:
            start_iter = self.txt_buff.get_iter_at_offset(m.start())
            end_iter = self.txt_buff.get_iter_at_offset(m.end())
            m_iters.append((start_iter, end_iter))
        return m_iters

    def read_config(self):
        self.conf_dir = os.sep.join(os.path.dirname(__file__).\
                                    split(os.sep)[:-1] +\
                                    ["config"])
        try:
            f = open(os.path.join(self.conf_dir, "syntax_hl"), 'r')
        except IOError:
            f = open(os.path.join("config", "syntax_hl"), 'r')
        finally:
            config = f.read()
            self.config = eval(config)
            f.close()

    def fill_combo(self):
        syntax = self.config.keys()
        self.syntax.append_text("-------")
        for item in syntax:
            self.syntax.append_text(item)
        self.syntax.set_active(0)

    def combo_hl(self, *args):
        syntax = self.syntax.get_active_text()
        c_syntax = self.config.get(syntax, "")
        self.filter.buf.set_text(c_syntax)
        self.filter.parse_and_highlight()
        self.filter.filter_logs()

    def select_string(self, s_pos, e_pos):
        s_iter = self.txt_buff.get_iter_at_offset(s_pos)
        e_iter = self.txt_buff.get_iter_at_offset(e_pos)
        self.log_text.scroll_to_iter(s_iter, 0)
        self.txt_buff.remove_tag(self.selection_tag,
            self.txt_buff.get_start_iter(),
            self.txt_buff.get_end_iter())
        #self.txt_buff.select_range(s_iter, e_iter)
        self.txt_buff.apply_tag(self.selection_tag, s_iter, e_iter)
        self.s = e_pos
        self.e = s_pos

    def search(self, start_pos, f):
        s_pos, e_pos = f(start_pos)
        if s_pos or e_pos:
            if s_pos >= 0:
                self.select_string(s_pos, e_pos)
        else:
            self.txt_buff.remove_tag(self.selection_tag,
                self.txt_buff.get_start_iter(),
                self.txt_buff.get_end_iter())
            #self.txt_buff.select_range(self.txt_buff.get_end_iter(),
                                       #self.txt_buff.get_end_iter())

    def b_search(self, start_pos):
        text = self.get_text().lower()[::-1]
        string_to_search = self.find_entry.get_text().decode('utf8').lower()[::-1]
        chars = len(string_to_search)
        ltext = len(text)
        if chars > 0:
            tf = text.find(string_to_search, ltext - start_pos)
            if tf > 0:
                pos = ltext - tf
                return pos - chars, pos
            else:
                return (-1, -1)
        else:
            return (None, None)

    def f_search(self, start_pos):
        text = self.get_text().lower()
        string_to_search = self.find_entry.get_text().decode('utf8').lower()
        chars = len(string_to_search)
        print chars
        if chars > 0:
            pos = text.find(string_to_search, start_pos)
            if pos > 0:
                return (pos, pos + chars)
            else:
                if start_pos == 0:
                    return (None, None)
                else:
                    return(-1, -1)
        else:
            return (None, None)

    def f_re_search(self, start_pos):
        text = self.get_text()
        string_to_search = self.find_entry.get_text().decode('utf8')
        if string_to_search:
            re_string = re.compile(string_to_search, re.U)
            searched = re_string.search(text[start_pos:])
            if searched:
                s_pos = searched.start() + start_pos
                e_pos = searched.end() + start_pos
                return (s_pos, e_pos)
            else:
                if start_pos == 0:
                    return (None, None)
                else:
                    return (-1, -1)
        else:
            return (None, None)

    def b_re_search(self, start_pos):
        text = self.get_text()
        string_to_search = self.find_entry.get_text().decode('utf8')
        if string_to_search:
            re_string = re.compile(string_to_search, re.U)
            searched = list(re_string.finditer(text[:start_pos]))
            if searched:
                s_pos = searched[-1].start()
                e_pos = searched[-1].end()
                return (s_pos, e_pos)
            else:
                return (-1, -1)
        else:
            return (None, None)

    def t_insert_search(self, *args):
        self.txt_buff.remove_tag(self.selection_tag,
            self.txt_buff.get_start_iter(),
            self.txt_buff.get_end_iter())
        if not self.re_toggle.get_active():
            self.search(0, self.f_search)
        else:
            self.search(0, self.f_re_search)

    def insert_search(self, *args):
        if not self.re_toggle.get_active():
            self.search(0, self.f_search)
        else:
            self.search(0, self.f_re_search)

    def prev_search(self, *args):
        if not self.re_toggle.get_active():
            self.search(self.e, self.b_search)
        else:
            self.search(self.e, self.b_re_search)

    def next_search(self, *args):
        if not self.re_toggle.get_active():
            self.search(self.s, self.f_search)
        else:
            self.search(self.s, self.f_re_search)

    def show_hl(self, btn):
        if btn.get_active():
            self.filter.show()
        else:
            self.filter.hide()

    def get_text(self):
        start = self.txt_buff.get_start_iter()
        end = self.txt_buff.get_end_iter()
        return self.txt_buff.get_text(start, end)

    def copy_log(self, *args):
        clipboard = gtk.clipboard_get("CLIPBOARD")
        self.txt_buff.select_range(self.txt_buff.get_start_iter(),
                                   self.txt_buff.get_end_iter())
        self.txt_buff.copy_clipboard(clipboard)
        self.txt_buff.select_range(self.txt_buff.get_end_iter(),
                                   self.txt_buff.get_end_iter())

    def save_to_file(self, *args):
        fchooser = gtk.FileChooserDialog("Save logs to file...", None,
            gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL,
            gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK), None)
        fchooser.set_current_name("_".join([os.path.basename(f) for f in
                                            self.files]))
        response = fchooser.run()
        if response == gtk.RESPONSE_OK:
            path = fchooser.get_filename()
            f = open(path, "w")
            f.write(self.get_text())
            f.close()
        fchooser.destroy()

    def highlight(self, col_str):
        self.col_str = col_str
        start = self.txt_buff.get_start_iter()
        end = self.txt_buff.get_end_iter()
        self.txt_buff.remove_all_tags(start, end)
        txt = self.txt_buff.get_text(start, end)
        for pattern in col_str[1]:
            fre = re.compile(pattern)
            for m in fre.finditer(txt):
                print m.end() - m.start()
                start_iter = self.txt_buff.get_iter_at_offset(m.start())
                end_iter = self.txt_buff.get_iter_at_offset(m.end())
                self.txt_buff.remove_all_tags(start_iter, end_iter)
                for tag in col_str[0][pattern]:
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
                        elif att == "s":
                            ntag.set_property("size", int(tag[1:]) *\
                                                      pango.SCALE)
                        elif att == "i":
                            ntag.set_property("style", pango.STYLE_ITALIC)
                    self.txt_buff.apply_tag(ntag, start_iter, end_iter)

    def open_file(self, *args):
        for f in self.files:
            threading.Thread(target=os.system,
                             args=("notepad %s" % f,)).start()


    def filling(self, date_, log_name_, type_):
        self.open_label.set_text("\n".join(self.files))
        self.info_label.set_markup('<big><b>%s</b></big>\n%s\n%s\n' % (date_,
                                                                     log_name_,
                                                                     type_))
        self.log_text.get_buffer().set_text(self.txt)
        self.highlight(self.col_str)
        self.log_text.grab_focus()
        self.s = 0
        self.e = len(self.txt)
        self.insert_search(None)
        self.procs = self.motion_text(self.txt)
        

    def fill(self):
        select = self.loglist.get_msg_by_rowids(self.iter)
        self.txt = "".join(select[4])
        self.files = set(select[3])
        dates = set(select[0])
        if len(dates) > 1:
            start = min(dates).strftime("%H:%M:%S.%f %d.%m.%Y")
            end = max(dates).strftime("%H:%M:%S.%f %d.%m.%Y")
            date_ = "%s - %s" % (start, end)
        else:
            date_ = select[0][0].strftime("%H:%M:%S.%f %d.%m.%Y")
        type_ = ("ERROR" in select[2]) and '<span foreground="red">ERROR</span>' or ""
        log_name_ = "\n".join(set(select[1]))
        self.filling(date_,log_name_,type_)
        

    def show_prev(self, *args):
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        path = self.model.get_string_from_iter(self.iter)
        if path == 0:
            return None
        prevPath = int(path) + 1
        try:
            self.iter = self.model.get_iter_from_string(str(prevPath))
        except ValueError:
            return
        self.selection.select_path(prevPath)
        self.view.scroll_to_cell(prevPath)
        self.fill()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    def show_next(self, *args):
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        path = self.model.get_string_from_iter(self.iter)
        if path == 0:
            return None
        prevPath = int(path) - 1
        if prevPath >= 0:
            self.iter = self.model.get_iter_from_string(str(prevPath))
            self.selection.select_path(prevPath)
            self.view.scroll_to_cell(prevPath)
            self.fill()
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)


class SeveralLogsWindow(LogWindow):
    def __init__(self, loglist, iter, sel):
        LogWindow.__init__(self, loglist, iter, sel)
        self.info_box.remove(self.updown_btns)

    def fill(self):
        model, pathlist = self.selection.get_selected_rows()
        dates = []
        text = []
        types = []
        log_names = []
        self.files = []
        prev_f = ""
        for p in reversed(pathlist):
            iter_ = model.get_iter(p)
            select = self.loglist.get_msg_by_rowids(iter_)
            dates.extend(select[0])
            log_names.extend(select[1])
            types.extend(select[2])
            files = select[3]
            txt = select[4]
            for n,f in enumerate(files):
                if prev_f == f:
                    text.append(txt[n])
                else:
                    text.append("%s:\n\n%s" % (f, txt[n]))
                prev_f = f
            self.files.extend(files)
        self.files = set(self.files)
        self.txt = "\n".join(text)
        type_ = ("ERROR" in types) and '<span foreground="red">ERROR</span>' or ""
        log_name_ = "\n".join(set(log_names))
        if len(dates) > 1:
            start = min(dates).strftime("%H:%M:%S.%f %d.%m.%Y")
            end = max(dates).strftime("%H:%M:%S.%f %d.%m.%Y")
            date_ = "%s - %s" % (start, end)
        else:
            date_ = select[0][0].strftime("%H:%M:%S.%f %d.%m.%Y")
        self.filling(date_,log_name_,type_)
