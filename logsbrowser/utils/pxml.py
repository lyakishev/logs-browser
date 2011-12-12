import os
from functools import partial

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
        #for line in split_by("%s<" % os.linesep, piece, 2):
        yield piece

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
    return line[:9] == '<![CDATA['

def need_to_prettify(line):
    return line.find('><', line.find('><')+1) > -1

def pretty_tag(indent, offset, sep, counter, tag):
    return "%s%s%s" % (sep, offset + counter*indent, tag)

def get_indent(string):
    for n, c in enumerate(string):
        if not c.isspace():
            return n*" "

def prettify_tag(tag, counter, open_flag, pretty_tag):
    if is_tag(tag):
        close = is_close(tag)
        if (is_empty(tag) or is_cdata(tag)) and not close:
            return pretty_tag(counter, tag), counter, 0
        else:
            open_  = is_open(tag)
            both = close and open_
            if both:
                return pretty_tag(counter, tag), counter, 0
            elif close:
                counter -= 1
                return (tag if open_flag else pretty_tag(counter, tag)), counter, 0
            elif open_:
                return pretty_tag(counter, tag), counter+1, 1
            else:
                return pretty_tag(counter, tag), counter, open_flag
    else:
        return tag, counter, open_flag

def prettify_line(line, indent, sep, counter, open_flag, ppretty_tag):
    line_indent = get_indent(line)
    tags = split_xml(line)
    pretty_xml, counter, open_flag = prettify_tag(tags.next(), counter, open_flag,
                                            partial(ppretty_tag, "", ""))
    pretty_tag_sep = partial(ppretty_tag, line_indent, sep)
    for tag in tags:
        ptag, counter, open_flag = prettify_tag(tag, counter, open_flag,
                                                    pretty_tag_sep)
        pretty_xml += ptag
    return (pretty_xml, 0 if line_indent else 1, counter, open_flag)

def pretty_parts(xml, indent, sep):
    counter = open_flag = 0
    ppretty_tag = partial(pretty_tag, indent)
    pretty_xml = ""
    for line in xml.splitlines(True):
        if need_to_prettify(line):
            p_xml, state, counter, open_flag = prettify_line(line, indent,
                                                                  sep, counter,
                                                                  open_flag,
                                                                  ppretty_tag)
            pretty_xml += p_xml
            if counter == 0:
                yield pretty_xml, state
                pretty_xml = ""
        else:
           if counter == 0:
               yield line, 0
               pretty_xml = ""
           else:
               pretty_xml += line

def prettify_xml(xml, indent="    ", sep=os.linesep):
    parts = list(pretty_parts(xml, indent, sep))
    xmls = len([1 for x in parts if x[1] == 1])
    if xmls > 1:
        prev = 0
        pretty_xml = ""
        for xml, state in parts:
            if state == 0:
                if prev == 0:
                    pretty_xml += xml
                else:
                    pretty_xml += ("\n%s" % xml)
                    prev = 0
            else:
                pretty_xml += ("\n%s" % xml)
                prev = 1
        return pretty_xml.lstrip()
    else:
        return "".join(x[0] for x in parts)

if __name__ == "__main__":
    import sys
    print prettify_xml(sys.stdin.read())
