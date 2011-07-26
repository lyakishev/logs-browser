#!/usr/bin/env python
import gtk
import gobject
from ui.logsviewer import LogsViewer
import multiprocessing as mp
from ui import dialogs
import sys
from threading import Thread
import config
if config.XMLRPC:
    from SimpleXMLRPCServer import SimpleXMLRPCServer

def xml_rpc_init(logsviewer):
    if config.XMLRPC:
        try:
            server = SimpleXMLRPCServer(("localhost", config.RPC_PORT), allow_none=True)
            server.register_introspection_functions()
            server.register_function(logsviewer.set_from_date, 'begin')
            server.register_function(logsviewer.set_to_date, 'end')
            Thread(target=server.serve_forever).start()
            return server
        except Exception:
            return None
    else:
        return None

def main():
    logsviewer = LogsViewer()
    server = xml_rpc_init(logsviewer)
    gtk.main()
    if server:
        server.server_close()

if __name__ == '__main__':
    sys.excepthook = dialogs.exception_dialog
    gobject.threads_init()
    mp.freeze_support()
    main()
    
