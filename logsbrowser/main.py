import gtk
from process import process
from ui.logsviewer import LogsViewer

if __name__ == '__main__':
    logsviewer = LogsViewer(process)
    gtk.main()
    
