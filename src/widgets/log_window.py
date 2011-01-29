#! -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import re
import xml.dom.minidom
import os
import threading
from widgets.color_parser import LogColorParser
import pango
import traceback

#xml_re = re.compile("<\?xml(.+)>")
xml_spl=re.compile(r"(<\?xml.+?>)")
xml_s = re.compile(r"<\?xml.+?>", re.DOTALL)
xml_s2 = re.compile(r"(?P<xml><.+>)(?P<other>.*)")
xml_new = re.compile(r"(<\?xml.+?><(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
xml_bad = re.compile(r"((?<!>)<(\w+).*?>.*?</\2>(?!<))", re.DOTALL)

class LogWindow:
    def __init__(self, model, view, iter, sel):
        self.model = model
        self.view = view
        self.selection = sel
        self.iter = iter
        self.popup = gtk.Window()
        self.popup.set_title("Log")
        self.popup.set_default_size(700,700)
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
        self.find_entry.connect("changed", self.search)
        find_entry_item = gtk.ToolItem()
        find_entry_item.add(self.find_entry)
        prev_btn = gtk.ToolButton(gtk.STOCK_GO_BACK)
        prev_btn.connect("clicked", self.prev_search)
        next_btn = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        next_btn.connect("clicked", self.next_search)
        re_toggle = gtk.CheckButton("regexp")
        re_toggle_item = gtk.ToolItem()
        re_toggle_item.add(re_toggle)
        sep2 = gtk.SeparatorToolItem()
        hl_btn = gtk.ToggleToolButton(gtk.STOCK_SELECT_COLOR)
        hl_btn.connect("toggled", self.show_hl)
        
        toolbar.insert(open_btn, 0)
        toolbar.insert(save_btn, 1)
        toolbar.insert(copy_btn, 2)
        toolbar.insert(sep1, 3)
        toolbar.insert(find_label_item,4)
        toolbar.insert(find_entry_item,5)
        toolbar.insert(prev_btn,6)
        toolbar.insert(next_btn,7)
        toolbar.insert(re_toggle_item,8)
        toolbar.insert(sep2, 9)
        toolbar.insert(hl_btn,10)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)

        self.filter = LogColorParser(self)

        self.selection_tag = self.txt_buff.create_tag("select")
        self.selection_tag.set_property("size",12*pango.SCALE)
        self.selection_tag.set_property("weight",pango.WEIGHT_BOLD)
        self.selection_tag.set_property("background",'#00F')
        self.selection_tag.set_property("foreground",'#FFF')

        self.paned = gtk.VBox()
        self.paned.pack_start(self.scr,True,True)
        self.paned.pack_start(self.filter,False,False, padding=5)

        self.box.pack_start(self.info_box, False, False, padding=10)
        self.box.pack_start(toolbar, False, False)
        self.box.pack_start(self.paned)
        self.tag_table = self.txt_buff.get_tag_table()
        self.col_str=({},[])
        self.fill()

        self.popup.show_all()
        self.filter.hide()

    def prev_search(self, *args):
        string_to_search = self.find_entry.get_text()
        if string_to_search:
            try:
                s,e = self.e.backward_search(string_to_search, gtk.TEXT_SEARCH_TEXT_ONLY)
            except TypeError:
               return
            else:
                self.log_text.scroll_to_iter(s,0)
                self.txt_buff.remove_tag(self.selection_tag,
                    self.txt_buff.get_start_iter(),
                    self.txt_buff.get_end_iter()
                )
                self.txt_buff.apply_tag(self.selection_tag,s,e)
                self.s = e
                self.e = s
        else:
            self.txt_buff.remove_tag(self.selection_tag,
                self.txt_buff.get_start_iter(),
                self.txt_buff.get_end_iter()
            )
            self.s = self.txt_buff.get_start_iter()
            self.e = self.txt_buff.get_end_iter()

    def next_search(self, *args):
        string_to_search = self.find_entry.get_text()
        if string_to_search:
            try:
                s,e = self.s.forward_search(string_to_search, gtk.TEXT_SEARCH_TEXT_ONLY)
            except TypeError:
                return
            else:
                self.log_text.scroll_to_iter(s,0)
                self.txt_buff.remove_tag(self.selection_tag,
                    self.txt_buff.get_start_iter(),
                    self.txt_buff.get_end_iter()
                )
                self.txt_buff.apply_tag(self.selection_tag,s,e)
                self.s = e
                self.e = s
        else:
            self.txt_buff.remove_tag(self.selection_tag,
                self.txt_buff.get_start_iter(),
                self.txt_buff.get_end_iter()
            )
            self.s = self.txt_buff.get_start_iter()
            self.e = self.txt_buff.get_end_iter()

    def search(self, *args):
        string_to_search = self.find_entry.get_text()
        if string_to_search:
            start = self.txt_buff.get_start_iter()
            try:
                s,e = start.forward_search(string_to_search, gtk.TEXT_SEARCH_TEXT_ONLY)
            except TypeError:
                return
            else:
                self.log_text.scroll_to_iter(s,0)
                self.txt_buff.remove_tag(self.selection_tag,
                    self.txt_buff.get_start_iter(),
                    self.txt_buff.get_end_iter()
                )
                self.txt_buff.apply_tag(self.selection_tag,s,e)
                self.s = e
                self.e = s
        else:
            self.txt_buff.remove_tag(self.selection_tag,
                self.txt_buff.get_start_iter(),
                self.txt_buff.get_end_iter()
            )
            self.s = self.txt_buff.get_start_iter()
            self.e = self.txt_buff.get_end_iter()
        

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
        pass

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
            fre = re.compile(pattern.decode('utf8'), re.U)
            for m in fre.finditer(txt.decode('utf8')):
                start_iter = self.txt_buff.get_iter_at_offset(m.start())
                end_iter = self.txt_buff.get_iter_at_offset(m.end())
                self.txt_buff.remove_all_tags(start_iter, end_iter)
                for tag in col_str[0][pattern]:
                    ntag = self.tag_table.lookup(tag)
                    if not ntag:
                        ntag = self.txt_buff.create_tag(tag)
                        att = tag[0]
                        if att == "f":
                            ntag.set_property("foreground",tag[1:])
                        elif att == "b":
                            if len(tag)>1:
                                ntag.set_property("background",tag[1:])
                            else:
                                ntag.set_property("weight",pango.WEIGHT_BOLD)
                        elif att == "s":
                            ntag.set_property("size",int(tag[1:])*pango.SCALE)
                        elif att == "i":
                            ntag.set_property("style",pango.STYLE_ITALIC)
                    self.txt_buff.apply_tag(ntag, start_iter, end_iter)

    def open_file(self, *args):
        file_to_open = self.model.get_value(self.iter, 4)
        threading.Thread(target=os.system, args=("notepad "+file_to_open,)).start()

    def fill(self):
        self.files = set([self.model.get_value(self.iter,4)])
        self.txt = "\n%s" % (
            self.model.get_value(self.iter, 5)
        )
        try:
            self.txt = self.txt.decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            self.txt = self.txt.decode('cp1251').encode('utf-8')
        self.open_label.set_text(self.model.get_value(self.iter,4))
        self.info_label.set_markup('<span background="%s"><big><b>%s</b></big></span>\n%s\n%s\n' % \
            (self.model.get_value(self.iter,6),\
            self.model.get_value(self.iter,0),\
            self.model.get_value(self.iter,2),
            self.model.get_value(self.iter,3) == "ERROR" and '<span foreground="red">ERROR</span>' or "",\
            ))
        self.log_text.get_buffer().set_text(self.pretty_xml(self.txt))
        self.highlight(self.col_str)
        self.log_text.grab_focus()
        self.s = self.txt_buff.get_start_iter()
        self.e = self.txt_buff.get_end_iter()


    def show_prev(self, *args):
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        path = self.model.get_string_from_iter(self.iter)
        if path == 0:
            return None
        prevPath = int(path)+1
        self.selection.select_path(prevPath)
        try:
            self.iter = self.model.get_iter_from_string(str(prevPath))
        except ValueError:
            pass
        self.view.scroll_to_cell(prevPath)
        self.fill()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    def show_next(self, *args):
        self.selection.set_mode(gtk.SELECTION_SINGLE)
        path = self.model.get_string_from_iter(self.iter)
        if path == 0:
            return None
        prevPath = int(path) -1
        self.selection.select_path(prevPath)
        try:
            self.iter = self.model.get_iter_from_string(str(prevPath))
        except ValueError:
            pass
        self.view.scroll_to_cell(prevPath)
        self.fill()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    def pretty_xml(self,text):
        def xml_pretty(m):
            txt = m.group()
            try:
                pretty_xml = xml.dom.minidom.parseString(txt.encode("utf-16")).toprettyxml()
            except xml.parsers.expat.ExpatError as xml_er:
                print traceback.format_exc()
                pretty_xml = txt.replace("><",">\n<")
            return "\n"+pretty_xml

        def xml_bad_pretty(m):
            txt = xml_pretty(m)
            new_txt = txt.splitlines()[2:]
            return "\n".join(new_txt)

        text = xml_bad.sub(xml_bad_pretty, text)
        return xml_new.sub(xml_pretty, text)

class SeveralLogsWindow(LogWindow):
    def __init__(self,model, view, iter, sel):
        LogWindow.__init__(self,model, view, iter, sel)
        self.info_box.remove(self.updown_btns)

    def show_next(self):
        pass

    def show_prev(self):
        pass

    def open_file(self, *args):
        for f in self.files:
            threading.Thread(target=os.system, args=("notepad "+f,)).start()

    def fill(self):
        model, pathlist = self.selection.get_selected_rows()
        text = []
        self.files = set()
        pathlist.reverse()
        for p in pathlist:
            iter = model.get_iter(p)
            self.files.add(model.get_value(iter,4))
        prev_f = ""
        for p in pathlist:
            iter = model.get_iter(p)
            f = model.get_value(iter,4)
            txt = model.get_value(iter, 5)
            try:
                txt = txt.decode('utf-8').encode('utf-8')
            except UnicodeDecodeError:
                txt = txt.decode('cp1251').encode('utf-8')
            if len(self.files) == 1:
                text.append("%s" % self.pretty_xml(txt))
            else:
                if prev_f == f:
                    text.append("%s" % self.pretty_xml(txt))
                else:
                    text.append("%s:\n\n%s" % (f, self.pretty_xml(txt)))
            prev_f = f
        self.open_label.set_text("\n".join(self.files))
        begin_it = model.get_iter(pathlist[-1])
        end_it = model.get_iter(pathlist[0])
        begin_date = model.get_value(begin_it, 0)
        end_date = model.get_value(end_it, 0)
        date = " - ".join([str(begin_date),str(end_date)])
        self.info_label.set_markup('<b>%s</b>' % date)
        self.full_text = "\n".join(text)
        self.log_text.get_buffer().set_text(self.full_text)
        self.highlight(self.col_str)
        self.log_text.grab_focus()

