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

import re
import xml.dom.minidom
from colorsys import *
import sys
from utils.text import convert_line_ends
from collections import OrderedDict

aggregate_functions = ['avg', 'count', 'group_concat', 'max', 'min', 'sum', 'total']

operators = OrderedDict([('---', ' '),
                ('REGEXP', 'NOT'),
                ('MATCH', 'NOT'),
                ('LIKE', 'NOT'),
                ('GLOB', 'NOT'),
                ('=', '!'),
                (">", ' '),
                ("<", ' '),
                ("CONTAINS", 'NOT'),
                ("ICONTAINS", 'NOT'),
                ("IREGEXP", 'NOT')
   ])

operator_functions = {"CONTAINS": ["contains", "not_contains"],
            "ICONTAINS": ["icontains", "not_icontains"],
            "IREGEXP": ["iregexp", "not_iregexp"]
}

xml_new = re.compile(r"(<\?xml.+?><(\w+).*?>.*?</\2>(?!<))")
xml_bad = re.compile(r"<.+?><.+?>")
xml_new_bad = re.compile(r"<(\w+).*?>.*?</\1>")


#TODO SPA, ProdUI
def xml_pretty(txt):
        try:
            xparse = xml.dom.minidom.parseString
            pretty_xml = xparse(txt.encode("utf-16")).toprettyxml()
        except xml.parsers.expat.ExpatError:
            pretty_xml = txt.replace("><", ">\n<")
        except Exception:
            pretty_xml = txt
        return pretty_xml

def parse_bad_xml(m):
    xml = m.group()
    if xml_bad.search(xml):
        ret_xml = xml_pretty('<?xml version="1.0" encoding="utf-16"?>'+m.group())
        return '\n'.join(ret_xml.splitlines()[1:])
    else:
        return xml

def parse_good_xml(m):
    return '\n'+xml_pretty(m.group())
    
def pretty_xml(t):
    if xml_bad.search(t):
        text = xml_new.sub(parse_good_xml, t)
        if xml_bad.search(text):
            text = xml_new_bad.sub(parse_bad_xml, text)
        return text.replace("&quot;", '"').replace("&gt;",">").replace("&lt;","<")
    return t

def pretty(t):
    return pretty_xml(convert_line_ends(t))

re_cache = {}
i_re_cache = {}


def regexp(pattern, field):
    re_obj = re_cache.get(pattern)
    if not re_obj:
        re_obj = re.compile(pattern)
        re_cache[pattern] = re_obj
    ret = re_obj.search(field)
    return True if ret else False

def iregexp(field, pattern):
    re_obj = i_re_cache.get(pattern)
    if not re_obj:
        re_obj = re.compile(pattern, re.I)
        re_cache[pattern] = re_obj
    ret = re_obj.search(field)
    return True if ret else False

def not_iregexp(field, pattern):
    re_obj = i_re_cache.get(pattern)
    if not re_obj:
        re_obj = re.compile(pattern, re.I)
        re_cache[pattern] = re_obj
    ret = re_obj.search(field)
    return False if ret else True

def icontains(field, text):
    return text.lower() in field.lower()

def not_icontains(field, text):
    return text.lower() not in field.lower()

def contains(field, text):
    return text in field

def not_contains(field, text):
    return text not in field

def regex(t, pattern, gr):
    re_obj = re_cache.get(pattern)
    if not re_obj:
        re_obj = re.compile(pattern)
        re_cache[pattern] = re_obj
    ret = re_obj.search(t)
    if ret:
        return ret.group(gr)
    else:
        return ""

def rmatch(pattern, field):
    pattern = '(\W|^)' + re.escape(pattern).replace('\*', '\w*') + '(\W|$)'
    re_obj = i_re_cache.get(pattern)
    if not re_obj:
        re_obj = re.compile(pattern, re.I)
        re_cache[pattern] = re_obj
    ret = re_obj.search(field)
    return True if ret else False

def intersct(lids1, lids2):
    s1 = str(lids1).split(',')
    s2 = str(lids2).split(',')
    return True if set(s1) & set(s2) else False

class AggError:
    
    error = 'ERROR'
    warning = 'WARNING'
    info = 'INFORMATION'

    def __init__(self):
        self.type_ = '?'

    def step(self, value):
        if value == self.error:
            self.type_ = value
        elif value == self.warning:
            if self.type_ != self.error:
                self.type_ = value
        elif value == self.info:
            if self.type_ != self.error and self.type_ != self.warning:
                self.type_ = value

    def finalize(self):
        return self.type_

class RowIDsList:
    def __init__(self):
        self.rowids = ""

    def step(self, value):
        self.rowids += ',%s' % value

    def finalize(self):
        return self.rowids[1:]

class ColorAgg:
    def __init__(self):
        self.colors = set()

    def step(self, value):
        self.colors.add('%s' % value)

    def finalize(self):
        return " ".join(self.colors)


class GroupLogname:
    def __init__(self):
        self.prev_logname = None
        self.count = 0

    def __call__(self, logname):
        if not self.prev_logname:
            self.prev_logname = logname
            return self.count
        if logname == self.prev_logname:
            return self.count
        else:
            self.count += 1
            self.prev_logname = logname
            return self.count

    def clear(self):
        self.__init__()

group_logname = GroupLogname()
