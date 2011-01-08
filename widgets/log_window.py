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

#xml_re = re.compile("<\?xml(.+)>")
xml_spl=re.compile(r"(<\?xml.+?>)")
xml_s = re.compile(r"<\?xml.+>", re.DOTALL)
xml_s2 = re.compile(r"(?P<xml><.+>)(?P<other>.*)")

class LogWindow:
    def __init__(self, model, view, iter, sel):
        self.model = model
        self.view = view
        self.selection = sel
        self.iter = iter
        self.popup = gtk.Window()
        self.popup.set_title("Log")
        self.popup.set_default_size(640,480)
        self.box = gtk.VBox()
        self.open_info_box = gtk.VBox()
        self.info_box = gtk.HBox()
        self.info_label = gtk.Label()
        self.info_button = gtk.Button()
        self.info_button.set_relief(gtk.RELIEF_NONE)
        self.info_button.connect('clicked', self.open_file)
        self.open_label = gtk.Label()
        self.info_button.add(self.open_label)
        self.info_box.pack_start(self.open_info_box)
        self.open_info_box.pack_start(self.info_label)
        self.open_info_box.pack_start(self.info_button)
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
        self.scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.log_text = gtk.TextView()
        self.txt_buff = self.log_text.get_buffer()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.scr.add(self.log_text)
        self.popup.add(self.box)
        self.filter_exp = gtk.Expander("Highlight")
        self.filter = LogColorParser(self)
        self.filter_exp.add(self.filter)
        self.box.pack_start(self.info_box, False, False, padding=10)
        self.box.pack_start(self.scr)
        self.box.pack_start(self.filter_exp, False,False)
        self.tag_table = self.txt_buff.get_tag_table()
        self.col_str=({},[])
        self.fill()
        self.popup.show_all()

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
        self.txt = "%s\n%s\n%s\n%s\n%s\n\n\n%s" % (
            self.model.get_value(self.iter, 0),
            self.model.get_value(self.iter, 1),
            self.model.get_value(self.iter, 2),
            self.model.get_value(self.iter, 3),
            self.model.get_value(self.iter, 4),
            self.model.get_value(self.iter, 5)
        )
        try:
            self.txt = self.txt.decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            self.txt = self.txt.decode('cp1251').encode('utf-8')
        self.open_label.set_text(self.model.get_value(self.iter,4))
        self.info_label.set_markup('<span background="%s"><big><b>%s</b></big></span>\n%s\n' % \
            (self.model.get_value(self.iter,6),\
            self.model.get_value(self.iter,0),\
            self.model.get_value(self.iter,3) == "ERROR" and '<span foreground="red">ERROR</span>' or "",\
            ))
        self.log_text.get_buffer().set_text(self.pretty_xml(self.txt))
        self.highlight(self.col_str)


    def show_prev(self, *args):
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

    def show_next(self, *args):
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

    def pretty_xml(self,text):
        def xml_pretty(m):
            txt = m.group()
            spl = xml_spl.split(txt)[1:]
            pr_xml = []
            for head, body in zip(spl[::2], spl[1::2]):
                xml_other = xml_s2.search(body).groupdict()
                true_xml = "".join([head, xml_other['xml']])
                pretty_xml = xml.dom.minidom.parseString(true_xml.encode("utf-16")).toprettyxml()
                pr_xml.append("".join([pretty_xml, xml_other['other']]))
                
            return "\n".join(pr_xml)

        try:
            return xml_s.sub(xml_pretty, text)
        except:
            return text

