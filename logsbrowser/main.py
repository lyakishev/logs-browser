import gtk
from process import process
from ui.logsviewer import LogsViewer

def main():
    logsviewer = LogsViewer(process)
    gtk.main()
    

if __name__ == '__main__':
    main()
    
