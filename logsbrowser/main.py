#!/usr/bin/env python
import gtk
import gobject
from ui.logsviewer import LogsViewer
import multiprocessing as mp
from ui import dialogs
import sys

def main():
    logsviewer = LogsViewer()
    gtk.main()
    

if __name__ == '__main__':
    sys.excepthook = dialogs.exception_dialog
    gobject.threads_init()
    mp.freeze_support()
    main()
    
