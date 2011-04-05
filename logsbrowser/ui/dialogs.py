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

def mwarning(parent, text):
    message_dialog = gtk.MessageDialog(parent,
        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
        gtk.BUTTONS_CLOSE, text)
    message_dialog.run()
    message_dialog.destroy()
