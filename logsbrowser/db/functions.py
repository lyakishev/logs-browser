import re
import xml.dom.minidom
from colorsys import *

xml_new = re.compile(r"(<\?xml.+?><(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
xml_bad = re.compile(r"((?<!>)<(\w+).*?>.*?</\2>(?!<))", re.DOTALL)
empty_lines = re.compile("^$")

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



def strip(t):
    return t.strip()

def regexp(pattern, field):
    ret = re.compile(pattern).search(field)
    return True if ret else False

def regex(t, pattern, gr):
    try:
        ret = re.compile(pattern).search(t).group(gr)
    except:
        pass
    else:
        return ret

class RowIDsList:
    def __init__(self):
        self.rowids = []

    def step(self, value):
        self.rowids.append(value)

    def finalize(self):
        return str(self.rowids)[1:-1]

class AggError:
    def __init__(self):
        self.type_ = '?'

    def step(self, value):
        if value == 'ERROR':
            self.type_ = 'ERROR'

    def finalize(self):
        return self.type_

class ColorAgg:
    def __init__(self):
        self.colors = []

    def circ_ave(self, a0, a1):
        r = (a0+a1)/2., ((a0+a1+360)/2.)%360 
        if min(abs(a1-r[0]), abs(a0-r[0])) < min(abs(a0-r[1]), abs(a1-r[1])):
            return r[0]
        else:
            return r[1]

    def step(self, value):
        if value != '#fff':
            c = gtk.gdk.color_parse(value)
            self.colors.append((c.red,c.green,c.blue))

    def finalize(self):
        if self.colors:
            new_colors = set([rgb_to_hsv(*c) for c in set(self.colors)])
            hue = reduce(self.circ_ave, [c[0]*360 for c in new_colors])/360.
            saturations = [c[1] for c in new_colors]
            sat = sum(saturations)/float(len(saturations))
            values = [c[2]/65535. for c in new_colors]
            value = sum(values)/float(len(values))
            mix_color=gtk.gdk.color_from_hsv(hue, sat, value)
            return mix_color.to_string()
        else:
            return '#fff'


