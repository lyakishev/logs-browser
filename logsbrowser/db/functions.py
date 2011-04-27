import re
import xml.dom.minidom
from colorsys import *

aggregate_functions = ['avg', 'count', 'group_concat', 'max', 'min', 'sum', 'total']

xml_new = re.compile(r"(<\?xml.+?><(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
xml_bad = re.compile(r"((?<!>)<(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
empty_lines = re.compile("^$")

#TODO SPA, ProdUI
def xml_pretty(m):
        txt = m.group()
        try:
            xparse = xml.dom.minidom.parseString
            pretty_xml = xparse(txt.encode("utf-16")).toprettyxml()
        except xml.parsers.expat.ExpatError:
            #print traceback.format_exc()
            pretty_xml = txt.replace("><", ">\n<")
        return "\n" + pretty_xml

def xml_bad_pretty(m):
    txt = xml_pretty(m)
    new_txt = txt.splitlines()[2:]
    return "\n".join(new_txt)

def pretty_xml(t):
    text = xml_bad.sub(xml_bad_pretty, t)
    text = empty_lines.sub("",xml_new.sub(xml_pretty, text))
    return text.replace("&quot;", '"').replace("&gt;",">").replace("&lt;","<")


def regexp(pattern, field):
    ret = re.compile(pattern).search(field)
    return True if ret else False

def iregexp(field, pattern):
    ret = re.compile(pattern, re.I).search(field)
    return True if ret else False

def regex(t, pattern, gr):
    ret = re.compile(pattern).search(t).group(gr)
    return ret

def rmatch(field, pattern):
    ret = re.compile('(\W|^)'+pattern+'(\W|$)', re.I).search(field)
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
        self.rowids = []

    def step(self, value):
        self.rowids.append(str(value))

    def finalize(self):
        return ','.join(self.rowids)

class ColorAgg:
    def __init__(self):
        self.colors = set()

    def step(self, value):
        self.colors.add(str(value))

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


    


        
        
