import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import re
import xml.dom.minidom

#xml_re = re.compile("<\?xml(.+)>")
xml_re=re.compile(r"((<\?xml.+>);?)+")

class LogWindow:
    def __init__(self, txt):
        self.popup = gtk.Window()
        self.popup.set_title("Log")
        self.popup.set_default_size(640,480)
        self.scr = gtk.ScrolledWindow()
        self.scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.popup_frame = gtk.Frame("Log")
        self.log_text = gtk.TextView()
        self.log_text.set_editable(False)
        self.log_text.set_wrap_mode(gtk.WRAP_CHAR)
        self.log_text.get_buffer().set_text(self.pretty_xml(txt))
        self.popup_frame.add(self.scr)
        self.scr.add(self.log_text)
        self.popup.add(self.popup_frame)
        self.popup.show_all()

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
