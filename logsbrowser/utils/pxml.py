import os
from functools import partial
#from utils.profiler import profile

#<?xml ?> move too
#pretty when both (optional)

def split_by(string, text, pos_offset):
    pos = 0
    npos = 0
    while 1:
        npos = text.find(string, pos)
        if npos == -1:
            break
        else:
            npos += pos_offset
            yield text[pos:npos]
        pos = npos
    yield text[pos:]

def split_xml(xml):
    for piece in split_by("><", xml, 1):
        for line in split_by("%s<" % os.linesep, piece, 2):
            yield line

def is_tag(line):
    return line.endswith('>') or line.startswith('<')

def is_empty(line):
    return (line[-2:] in ('/>', "?>")) or (line[:4] == "<!--")

def is_close(line):
    return "</" in line

def is_open(line):
    start = line.find("<")
    if start >= 0:
        return (start + 1) != line.find("/")
    else:
        return False

def is_cdata(line):
    return line.startswith('<![CDATA[')

def is_close_or_open(line):
    return is_close(line), is_open(line)

def need_to_prettify(line):
    return line.count("><") > 1

def pretty_tag(sep, indent, counter, tag):
    return "%s%s%s" % (sep, counter*indent, tag)

def plain_text(sep, tag):
    return "%s%s" % ("", tag)

def prettify_xml(xml, indent="    ", sep=os.linesep):
    ppretty_tag = partial(pretty_tag, sep, indent)
    pretty_xml = ""
    counter = 0
    open_flag = 0
    first_tag = 1
    for line in xml.splitlines(True):
        if need_to_prettify(line):
            for tag in split_xml(line):
                if is_tag(tag):
                    if is_empty(tag) or is_cdata(tag):
                        if first_tag:
                            pretty_xml += pretty_tag("", indent, counter, tag)
                        else:
                            pretty_xml += ppretty_tag(counter, tag)
                        open_flag = 0
                    else:
                        close, open_  = is_close_or_open(tag)
                        both = close and open_
                        if both:
                            pretty_xml += ppretty_tag(counter, tag)
                            open_flag = 0
                        elif close:
                            counter -= 1
                            if open_flag:
                                pretty_xml += tag
                            else:
                                pretty_xml += ppretty_tag(counter, tag)
                            open_flag = 0
                        elif open_:
                            if first_tag:
                                pretty_xml += pretty_tag("", indent, counter, tag)
                            else:
                                pretty_xml += ppretty_tag(counter, tag)
                            counter += 1
                            open_flag = 1
                        else:
                            pretty_xml += ppretty_tag(counter, tag)
                    first_tag = 0
                else:
                    pretty_xml += tag
        else:
            pretty_xml += line
            first_tag = 1
    return pretty_xml.lstrip()

if __name__ == "__main__":
    import sys
    print prettify_xml(sys.stdin.read())
