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



