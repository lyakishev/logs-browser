import pyHook
import pythoncom
from multiprocessing import Process
from net_time import GetTrueTime


class DetectClick(Process):
    def __init__(self, click_time):
        Process.__init__(self)
        self.click_time = click_time

    def onclick(self, event):
        self.click_time.value = GetTrueTime()
        raise SystemExit

    def run(self):
        hook_manager = pyHook.HookManager()
        hook_manager.SubscribeMouseAllButtonsDown(self.onclick)
        hook_manager.HookMouse()
        pythoncom.PumpMessages()
        hook_manager.UnhookMouse()
