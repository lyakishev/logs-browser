#!/usr/bin/env python
import gtk
from ui.logsviewer import LogsViewer
import multiprocessing as mp

def main():
    logsviewer = LogsViewer()
    gtk.main()
    

if __name__ == '__main__':
    mp.freeze_support()
    main()
    
