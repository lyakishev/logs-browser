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

# -*- coding: utf8 -*-

import traceback
import gio
import gobject
import gtk
import pygtk
pygtk.require("2.0")


def merror(text):
    md = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                           buttons=gtk.BUTTONS_CANCEL, message_format=text)
    md.run()
    md.destroy()


def exception_dialog(type_, value, tb):
    dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                               buttons=gtk.BUTTONS_CLOSE)
    dialog.set_markup("%s" % '\n'.join(
        traceback.format_exception_only(type_, value)))
    info = gtk.Expander('Stack trace')
    scr = gtk.ScrolledWindow()
    textview = gtk.TextView()
    textview.set_editable(False)
    scr.add(textview)
    info.add(scr)
    textview.get_buffer().set_text('%s' % '\n'.join(traceback.format_tb(tb)))
    dialog.vbox.pack_end(info, True, True)
    dialog.show_all()
    dialog.run()
    dialog.destroy()


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


if __name__ == "__main__":
    import sys
    sys.excepthook = exception_dialog
