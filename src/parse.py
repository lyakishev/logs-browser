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

PREFIX = r"[^ ]*?[ ]?\[?"
FORMATS = [
    "".join([r"(?P<year1>\d{4})[-.]",
            r"(?P<month1>\d{2})[-.]",
            r"(?P<day1>\d{2}) "]),
    "".join([r"(?P<day2>\d{2})[.-]",
             r"(?P<month2>\d{2})[.-]",
             r"(?P<year2>\d{4}) "]),
    "".join([r"(?<!\d)(?P<day3>\d{2})[.-]",
             r"(?P<month3>\d{2})[.-]",
             r"(?P<short_year3>\d{2}) "])]

SUFFIX = "".join([r"(?P<hour>\d{1,2}):"
         r"(?P<min>\d{2}):",
         r"(?P<sec>\d{2})",
         r"[,.]?(?P<ms>\d{,6})"])

COMMON_PARSER = re.compile(PREFIX + "(" + "|".join(FORMATS) + ")?" + SUFFIX)

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
    for i in ["year", "month", "day"]:
        pformat = pformat.replace(i + str(format_number), i)
    return pformat


def define_format(line):
    """Define format by check number in searched named groups"""
    parsed_line = COMMON_PARSER.search(line)
    if parsed_line:
        parsed_line_dict = parsed_line.groupdict()
        for format_number in range(1, len(FORMATS) + 1):
            if parsed_line_dict["day%d" % format_number]:
                return re.compile(PREFIX +\
                                  clear_format(FORMATS[format_number-1],
                                               format_number) +\
                                  SUFFIX)
        return re.compile(PREFIX+SUFFIX)
    parsed_line = LOG4J.search(line)
    if parsed_line:
        return LOG4J
    return None


def parse_logline_re(line, cdate, re_obj):
    """Get datetime from string"""
    parsed_line = re_obj.match(line)
    if parsed_line:
        if re_obj is not LOG4J:
            groups = parsed_line.group
            millisecs = groups("ms")
            millisecs = int((millisecs+'000')[:6] if millisecs else 0)
            try:
                day = int(groups("day"))
            except IndexError:
                year = cdate.year
                month = cdate.month
                day = cdate.day
            else:
                month = int(groups("month"))
                try:
                    year = int(groups("year"))
                except IndexError:
                    year = int(groups("short_year"))+2000
            return datetime(year,month,day,
                                  int(groups('hour')),
                                  int(groups('min')),
                                  int(groups('sec')),
                                  millisecs)
        else:
            tstamp = parsed_line.group('datetime')
            return datetime.fromtimestamp(float(tstamp) / 1000)
    else:
        return None
