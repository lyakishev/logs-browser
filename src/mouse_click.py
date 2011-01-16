import pyHook
import pythoncom
import datetime
import time
from multiprocessing import Process
from net_time import *


class DetectClick(Process):
    def __init__(self, ct):
        Process.__init__(self)
        self.click_time = ct

    def onclick(self, event):
        self.click_time.value = get_true_time()
        raise SystemExit

    def run(self):
        hm = pyHook.HookManager()
        hm.SubscribeMouseAllButtonsDown(self.onclick)
        hm.HookMouse()
        pythoncom.PumpMessages()
        hm.UnhookMouse()
