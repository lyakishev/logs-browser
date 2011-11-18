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

import pyHook
import pythoncom
from multiprocessing import Process
from net_time import get_true_time


class DetectClick(Process):
    def __init__(self, click_time):
        Process.__init__(self)
        self.click_time = click_time

    def onclick(self, event):
        self.click_time.value = get_true_time()
        raise SystemExit

    def run(self):
        hook_manager = pyHook.HookManager()
        hook_manager.SubscribeMouseAllButtonsDown(self.onclick)
        hook_manager.HookMouse()
        pythoncom.PumpMessages()
        hook_manager.UnhookMouse()
