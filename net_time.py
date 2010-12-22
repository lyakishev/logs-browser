from datetime import datetime
import subprocess
import re

true_time_re = re.compile(r"\d{2}\.\d{2}.\d{4}\s\d{2}:\d{2}:\d{2}")

def get_true_time():
    time_string = subprocess.check_output(r"net time \\msk-app-v0190")
    return  datetime.strptime(true_time_re.search(time_string).group(0), "%d.%m.%Y %H:%M:%S")
