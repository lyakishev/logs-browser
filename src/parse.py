"""This module cleans file names from junk and get datetime from log's
string"""

from datetime import datetime
import re
import os



DIGITS_IN_NAME = re.compile(r"(?<=[a-zA-Z])\d(?=[a-zA-Z._])|\s|[A-Za-z._-]")
T_IN_NAME = re.compile(r"(?<=\d)T(?=\d)")
LITERAL_AT_BEGIN_END_LINE = re.compile("^[._-]+|[._-]+$")
REPEATED_LITERALS = re.compile(r"([._-]){2,}")
REPEATED_EXTENSION = re.compile(r"(\.[a-zA-Z]{3})\1+")
NULL_WORD = re.compile(r"(?<![A-Za-z])null(?![A-Za-z])")
LONG_EXTENSION = re.compile(r"[A-Za-z_]{7,}")

PREFIX = r"^(Time:|\[?\w+\]?|\w+|\(\w+->\w+\))?\s*\[?"
FORMATS = [
    "".join([r"(?P<year1>\d{4})[.-]",
            r"(?P<month1>\d{2})[.-]",
            r"(?P<day1>\d{2})",
            r"\s*(?P<hour1>\d{2})[:]",
            r"(?P<min1>\d{2})[:]",
            r"(?P<sec1>\d{2})",
            r"([,.](?P<ms1>\d+))?"]),
    "".join([r"(?P<day2>\d{2})[.-]",
             r"(?P<month2>\d{2})[.-]",
             r"(?P<year2>\d{4})",
             r"\s*(?P<hour2>\d{,2})[:]",
             r"(?P<min2>\d{2})[:]",
             r"(?P<sec2>\d{2})",
             r"([,.](?P<ms2>\d+))?"]),
    "".join([r"(?P<hour3>\d{2})[:]",
             r"(?P<min3>\d{2})[:]",
             r"(?P<sec3>\d{2})",
             r"[,.](?P<ms3>\d+)"]),
    "".join([r"(?<!\d)(?P<day4>\d{2})[.-]",
             r"(?P<month4>\d{2})[.-]",
             r"(?P<year4>\d{2})",
             r"\s*(?P<hour4>\d{,2})[:]",
             r"(?P<min4>\d{2})[:]",
             r"(?P<sec4>\d{2})",
             r"([,.](?P<ms4>\d+))?"]),
]
SUFFIX = r"\]?\s*(?P<msg>.+)"

COMMON_PARSER = re.compile(PREFIX + "(" + "|".join(FORMATS) + ")" + SUFFIX)

LOG4J = re.compile("".join([r'^<log4j.+',
                            r'timestamp="(?P<datetime>\d+)"',
                            r'.+</log4j:event>']))


def parse_filename(path):
    """Parse file name: remove digits, "junk" literals etc."""
    fname = T_IN_NAME.sub('', path)
    fname = "".join(DIGITS_IN_NAME.findall(fname))
    fname = REPEATED_EXTENSION.sub(r'\1', fname)
    fname = LITERAL_AT_BEGIN_END_LINE.sub('', fname)
    name, ext = os.path.splitext("a." + fname)
    name = LITERAL_AT_BEGIN_END_LINE.sub('', name[2:])
    name = REPEATED_LITERALS.sub(r'\1', name)
    name = NULL_WORD.sub("", name)
    return (name, ext[1:].lower())


def clear_format(pformat, format_number):
    """Remove numbers from format string"""
    for i in ["year", "month", "day", "hour", "min", "sec", "ms"]:
        pformat = pformat.replace(i + str(format_number), i)
    return pformat


def define_format(line):
    """Define format by check number in searched named groups"""
    parsed_line = COMMON_PARSER.search(line)
    if parsed_line:
        parsed_line_dict = parsed_line.groupdict()
        for format_number in range(1, len(FORMATS) + 1):
            if parsed_line_dict["hour%d" % format_number]:
                return re.compile(PREFIX +\
                                  clear_format(FORMATS[format_number-1],
                                               format_number) +\
                                  SUFFIX)
    parsed_line = LOG4J.search(line)
    if parsed_line:
        return LOG4J
    return None


def parse_logline_re(line, cdate, re_obj):
    """Get datetime from string"""
    parsed_line = re_obj.match(line)
    if re_obj != LOG4J:
        if parsed_line:
            paresd_dict = parsed_line.groupdict()
            millisecs = paresd_dict["ms"]
            millisecs = int(millisecs and str(1000 * int(millisecs))[:6] or 0)
            year = paresd_dict.get("year")
            if year:
                if len(year) != 2:
                    year = int(year)
                else:
                    year = int("20" + year)
            else:
                year = cdate.tm_year
            log_datetime = datetime(year,
                          int(paresd_dict.get("month", cdate.tm_mon)),
                          int(paresd_dict.get("day", cdate.tm_mday)),
                          int(paresd_dict["hour"]),
                          int(paresd_dict["min"]),
                          int(paresd_dict["sec"]),
                          millisecs)
            return (log_datetime, paresd_dict['msg'])
        else:
            return None
    else:
        if parsed_line:
            tstamp = parsed_line.group('datetime')
            log_datetime = datetime.fromtimestamp(float(tstamp) / 1000)
            return (log_datetime, line)
        else:
            return None
