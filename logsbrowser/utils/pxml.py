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

def pretty_tag(sep, indent, f, counter, tag):
    return "%s%s%s" % (sep, f(counter, indent), tag)

def plain_text(sep, tag):
    return "%s%s" % ("", tag)

def get_indent(string):
    for n, c in enumerate(string):
        if not c.isspace():
            return n*" "

def prettify_xml(xml, indent="    ", sep=os.linesep):
    pretty_tag_sep = partial(pretty_tag, sep, indent)
    pretty_tag_no_sep = partial(pretty_tag, "", indent, lambda i,c: i*c)
    pretty_xml = ""
    counter = 0
    open_flag = 0
    first_tag = 1
    for line in xml.splitlines(True):
        if need_to_prettify(line):
            pretty_tag_line_indent = partial(pretty_tag_sep, lambda i,c: get_indent(line)+i*c)
            pretty_tag_first_flag = lambda ff: pretty_tag_no_sep if ff else pretty_tag_line_indent
            for tag in split_xml(line):
                if is_tag(tag):
                    close = is_close(tag)
                    if (is_empty(tag) or is_cdata(tag)) and not close:
                        pretty_xml += pretty_tag_first_flag(first_tag)(counter, tag)
                        open_flag = 0
                    else:
                        open_  = is_open(tag)
                        both = close and open_
                        if both:
                            pretty_xml += pretty_tag_line_indent(counter, tag)
                            open_flag = 0
                        elif close:
                            counter -= 1
                            if open_flag:
                                pretty_xml += tag
                            else:
                                pretty_xml += pretty_tag_line_indent(counter, tag)
                            open_flag = 0
                        elif open_:
                            pretty_xml += pretty_tag_first_flag(first_tag)(counter, tag)
                            counter += 1
                            open_flag = 1
                        else:
                            pretty_xml += pretty_tag_line_indent(counter, tag)
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
