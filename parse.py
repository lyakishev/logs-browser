from datetime import datetime, timedelta
import re


nums_in_filename = re.compile(r"[_.-]?((?<![a-zA-Z])\d(?![a-zA-Z]))+[_.-]?")

def parse_filename(path):
    fnwonums = nums_in_filename.sub('', path)
    fnparts = fnwonums.split('.')
    return (".".join(fnparts[:-1]) , fnparts[-1].lower())

line_re = re.compile(r"^(\[?\w+\]?|\w+)?\s*\[?"
r"((?P<year1>\d{4})[.-](?P<month1>\d{2})[.-](?P<day1>\d{2})\s*(?P<hour1>\d{2})[:](?P<min1>\d{2})[:](?P<sec1>\d{2})([,.](?P<ms1>\d+))?|"
r"(?P<day2>\d{2})[.-](?P<month2>\d{2})[.-](?P<year2>\d{4})\s*(?P<hour2>\d{2})[:](?P<min2>\d{2})[:](?P<sec2>\d{2})([,.](?P<ms2>\d+))?|"
r"(?P<hour3>\d{2})[:](?P<min3>\d{2})[:](?P<sec3>\d{2})[,.](?P<ms3>\d+))\]?\s*(?P<msg>.+)")

def parse_logline_re(line, cdate):
    parsed_line = line_re.search(line)
    if parsed_line:
        pd = parsed_line.groupdict()
        for n in [1,2,3]:
            if pd["hour%d" % n]:
                ms = pd["ms%d" % n]
                ms = int(ms and str(1000*int(ms))[:6] or 0)
                if pd.get("year%d" % n, None):
                    dt = datetime(int(pd["year%d" % n]),
                                  int(pd["month%d" %n]),
                                  int(pd["day%d" %n]),
                                  int(pd["hour%d" %n]),
                                  int(pd["min%d" %n]),
                                  int(pd["sec%d" %n]),
                                  ms
                    )
                else:
                    dt = datetime(cdate.tm_year, cdate.tm_mon, \
                        cdate.tm_mday, int(pd["hour%d" % n]), \
                        int(pd["min%d" % n]), int(pd["sec%d" % n]), ms)
            else:
                continue
        return (dt, pd['msg'])
    else:
        return None
    


