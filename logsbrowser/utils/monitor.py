import gio
import gobject

class ConfigMonitor:
    def __init__(self, config_file):
        self.conf = config_file
        self.gfile = gio.File(path=config_file)
        self.monitor = self.gfile.monitor_file()

    def register_action(self, func):
        def callback(filemonitor, file_, other_file, event_type):
            if event_type == gio.FILE_MONITOR_EVENT_CHANGED:
                gobject.idle_add(func)
        self.monitor.connect("changed", callback)



