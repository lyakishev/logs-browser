# -*- coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import gio


def merror(text):
    md = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                           buttons=gtk.BUTTONS_CANCEL, message_format=text)
    md.run()
    md.destroy()
