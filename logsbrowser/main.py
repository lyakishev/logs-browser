#!/usr/bin/env python
import gtk
import gobject
from ui.logsviewer import LogsViewer
import multiprocessing as mp

def main():
    logsviewer = LogsViewer()
    gtk.main()
    

if __name__ == '__main__':
    gobject.threads_init()
    mp.freeze_support()
    main()
    
