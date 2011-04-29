import re
import xml.dom.minidom
from colorsys import *
import sys

aggregate_functions = ['avg', 'count', 'group_concat', 'max', 'min', 'sum', 'total']

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


if __name__ == '__main__':
    s1 = '''2010-12-05 14:36:05,153 [1] DEBUG OrderManagement.Utils.Logging.LoggerFactory
=======================================
<CreateRequestParameters xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><TariffPlanIdNew>11</TariffPlanIdNew><Msisdn>79167677425</Msisdn><TerminalDeviceId>5980</TerminalDeviceId><IsFreePrice>false</IsFreePrice><IsMakeInvoice>false</IsMakeInvoice><IpAddress>172.20.64.254</IpAddress><SalePointCode /><Comment>test</Comment><IsSplitPersonalAccount>true</IsSplitPersonalAccount><PaymentAmount>0</PaymentAmount><MoveAmount>352.56984</MoveAmount><CustomerProcessId xsi:nil="true" /></CreateRequestParameters>''' 
    print pretty_xml(s1)
