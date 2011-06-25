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

def responseToDialog(entry, dialog, response):
    dialog.response(response)

def save_dialog():
    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK_CANCEL,
        None)
    dialog.set_markup('Please enter <b>name</b>:')
    entry = gtk.Entry()
    entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label("Name:"), False, 5, 5)
    hbox.pack_end(entry)
    dialog.vbox.pack_end(hbox, True, True, 0)
    dialog.show_all()
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
        text = entry.get_text()
    else:
        text = 0
    dialog.destroy()
    return text
