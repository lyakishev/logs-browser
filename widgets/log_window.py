#! -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import re
import xml.dom.minidom
import os
import threading

#xml_re = re.compile("<\?xml(.+)>")
xml_re=re.compile(r"((<\?xml.+>);?)+")

class LogWindow:
    def __init__(self, model, iter, sel):
        self.model = model
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
        self.info_box.pack_start(self.updown_btns)
        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.log_text = gtk.TextView()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        self.scr.add(self.log_text)
        self.popup.add(self.box)
        self.box.pack_start(self.info_box, False, False, padding=10)
        self.box.pack_start(self.scr)
        self.fill()
        self.popup.show_all()

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
        self.open_label.set_text(self.model.get_value(self.iter,4))
        self.info_label.set_markup("<big><b>%s</b></big>\n%s\n" % \
            (self.model.get_value(self.iter,0),\
            self.model.get_value(self.iter,3) == "ERROR" and '<span foreground="red">ERROR</span>' or "",\
            ))
        self.log_text.get_buffer().set_text(self.pretty_xml(self.txt))

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
        self.fill()

    def pretty_xml(self,text):
        def xml_pretty(m):
            new_xml = []
            try:
                for xml_gr in m.groups():
                    utf16xml = xml_gr.encode("utf-16")
                    new_xml.append(xml.dom.minidom.parseString(utf16xml).toprettyxml())
                return ";\n".join(new_xml)
            except:
                return "".join(m.groups())

        return xml_re.sub(xml_pretty, text)
