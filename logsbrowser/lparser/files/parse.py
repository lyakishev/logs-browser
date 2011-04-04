"""This module cleans file names from junk and get datetime from log's
string"""

from datetime import datetime
import re
import os

_prefix = r"[^ ]*?[ ]?\[?"
_formats = [
    "".join([r"(?P<year1>\d{4})[-.]",
            r"(?P<month1>\d{2})[-.]",
            r"(?P<day1>\d{2}) "]),
    "".join([r"(?P<day2>\d{2})[.-]",
             r"(?P<month2>\d{2})[.-]",
             r"(?P<year2>\d{4}) "]),
    "".join([r"(?<!\d)(?P<day3>\d{2})[.-]",
             r"(?P<month3>\d{2})[.-]",
             r"(?P<short_year3>\d{2}) "]),
    "".join([r"(?P<month4>\d{2})[/]",
             r"(?P<day4>\d{2})[/]",
             r"(?P<year4>\d{4}) "])]

_suffix = "".join([r"(?P<hour>\d{1,2}):"
         r"(?P<min>\d{2}):",
         r"(?P<sec>\d{2})",
         r"[,.]?(?P<ms>\d{,6})"])

_common_parser = re.compile(_prefix + "(" + "|".join(_formats) + ")?" + _suffix)

_log4j = re.compile("".join([r'^<log4j.+',
                            r'timestamp="(?P<datetime>\d+)"',
                            r'.+</log4j:event>']))


def clear_format(pformat, format_number):
    """Remove numbers from format string"""
    for i in ["year", "month", "day"]:
        pformat = pformat.replace(i + str(format_number), i)
    return pformat


def define_format(line):
    """Define format by check number in searched named groups"""
    parsed_line = _common_parser.search(line)
    if parsed_line:
        parsed_line_dict = parsed_line.groupdict()
        for format_number in range(1, len(_formats) + 1):
            if parsed_line_dict["day%d" % format_number]:
                return re.compile(_prefix +\
                                  clear_format(_formats[format_number-1],
                                               format_number) +\
                                  _suffix)
        return re.compile(_prefix+_suffix)
    parsed_line = _log4j.search(line)
    if parsed_line:
        return _log4j
    return None


def parse_logline(line, cdate, re_obj):
    """Get datetime from string"""
    parsed_line = re_obj.match(line)
    if parsed_line:
        if re_obj is not _log4j:
            groups = parsed_line.group
            millisecs = groups("ms") or '0'
            try:
                day = groups("day")
            except IndexError:
                year = cdate.year
                month = "%02d" % cdate.month
                day = "%02d" % cdate.day
            else:
                month = groups("month")
                try:
                    year = groups("year")
                except IndexError:
                    year = '20'+groups("short_year")
            return "%s-%s-%s %02d:%s:%s.%s" % (year, month, day,
                                  int(groups('hour')),
                                  groups('min'),
                                  groups('sec'),
                                  millisecs)
        else:
            tstamp = parsed_line.group('datetime')
            return datetime.fromtimestamp(float(tstamp) / 1000).isoformat(' ')
    else:
        return None
