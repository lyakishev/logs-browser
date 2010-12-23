from datetime import datetime, timedelta
import subprocess
import re

true_time_re = re.compile(r"\d{2}\.\d{2}.\d{4}\s\d{2}:\d{2}:\d{2}")

TimeDelta = timedelta(0)

def get_true_time():
    global TimeDelta
    try:
        time_string = subprocess.check_output(r"net time \\msk-app-v0190")
    except:
        server_time = datetime.now() + TimeDelta
    else:
        server_time = datetime.strptime(true_time_re.search(time_string).group(0), "%d.%m.%Y %H:%M:%S")
        TimeDelta = server_time - datetime.now()
    finally:
        return server_time
