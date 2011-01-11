from datetime import datetime, timedelta
import re
import os


nums_in_filename = re.compile(r"[_.-]?((?<![a-zA-Z])\d(?![a-zA-Z]))+[_.-]?")

def parse_filename(path):
    name, ext = os.path.splitext(path)
    fname = nums_in_filename.sub('', name)
    return (fname, ext[1:].lower())

prefix = r"^(Time:|\[?\w+\]?|\w+|\(\w+->\w+\))?\s*\[?"
formats = [
    r"(?P<year1>\d{4})[.-](?P<month1>\d{2})[.-](?P<day1>\d{2})\s*(?P<hour1>\d{2})[:](?P<min1>\d{2})[:](?P<sec1>\d{2})([,.](?P<ms1>\d+))?",
    r"(?P<day2>\d{2})[.-](?P<month2>\d{2})[.-](?P<year2>\d{4})\s*(?P<hour2>\d{,2})[:](?P<min2>\d{2})[:](?P<sec2>\d{2})([,.](?P<ms2>\d+))?",
    r"(?P<hour3>\d{2})[:](?P<min3>\d{2})[:](?P<sec3>\d{2})[,.](?P<ms3>\d+)",
    r"(?P<day4>\d{2})[.-](?P<month4>\d{2})[.-](?P<year4>\d{2})\s*(?P<hour4>\d{,2})[:](?P<min4>\d{2})[:](?P<sec4>\d{2})([,.](?P<ms4>\d+))?",
]
suffix = r"\]?\s*(?P<msg>.+)"


common_parser = re.compile(prefix+"("+"|".join(formats)+")"+suffix)

xml_format = re.compile(r'^<log4j.+timestamp="(?P<datetime>\d+)".+</log4j:event>')

def clear_format(pformat, n):
    for i in ["year","month","day","hour","min","sec","ms"]:
        pformat = pformat.replace(i+str(n), i)
    return pformat

def define_format(line):
    parsed_line = common_parser.search(line)
    if parsed_line:
        pd = parsed_line.groupdict()
        for n in range(1,len(formats)+1):
            if pd["hour%d" % n]:
                return re.compile(prefix+clear_format(formats[n-1],n)+suffix)
    parsed_line = xml_format.search(line)
    if parsed_line:
        return xml_format
    return None

def parse_logline_re(line, cdate, re_obj):
    parsed_line = re_obj.search(line)
    if re_obj != xml_format:
        if parsed_line:
            pd = parsed_line.groupdict()
            ms = pd["ms"]
            ms = int(ms and str(1000*int(ms))[:6] or 0)
            year = pd.get("year", None)
            if year:
                if len(year) != 2:
                    year = int(year)
                else:
                    year = int("20"+year)
            else:
                year = cdate.tm_year
            dt = datetime(year,
                          int(pd.get("month", None) or cdate.tm_mon),
                          int(pd.get("day", None) or cdate.tm_mday),
                          int(pd["hour"]),
                          int(pd["min"]),
                          int(pd["sec"]),
                          ms)
            return (dt, pd['msg'])
        else:
            return None
    else:
        if parsed_line:
            tstamp = parsed_line.group('datetime')
            dt = datetime.fromtimestamp(float(tstamp)/1000)
            return (dt, line)
        else:
            return None
        
    


