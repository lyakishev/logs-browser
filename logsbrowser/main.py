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

#!/usr/bin/env python
import gtk
import gobject
from ui.logsviewer import LogsViewer
import multiprocessing as mp
from ui import dialogs
import sys
# from threading import Thread
import config
# if config.XMLRPC:
#    from SimpleXMLRPCServer import SimpleXMLRPCServer

# def xml_rpc_init(logsviewer):
#    if config.XMLRPC:
#        try:
#            server = SimpleXMLRPCServer(("localhost", config.RPC_PORT), allow_none=True)
#            server.register_introspection_functions()
#            server.register_function(logsviewer.set_from_date, 'begin')
#            server.register_function(logsviewer.set_to_date, 'end')
#            Thread(target=server.serve_forever).start()
#            return server
#        except Exception:
#            return None
#    else:
#        return None


def main():
    logsviewer = LogsViewer()
    # server = xml_rpc_init(logsviewer)
    gtk.main()
    # if server:
    #    server.server_close()


if __name__ == '__main__':
    sys.excepthook = dialogs.exception_dialog
    mp.freeze_support()
    main()
