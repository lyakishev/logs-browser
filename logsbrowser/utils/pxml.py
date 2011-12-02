import os
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

def prettify_xml(xml, indent="    "):
    pretty_xml = ""
    counter = 0
    open_flag = 0
    #import pdb
    #pdb.set_trace()
    for line in split_xml(xml):
        if line.startswith('<'):
            empty = line[-2:] in ('/>', "?>")
            if empty:
                pretty_xml += "%s%s%s" % (os.linesep, counter*indent, line)
                open_flag = 0
            else:
                close = "</" in line
                open_ = line[1] != "/"
                both = close and open_
                if both:
                    pretty_xml += "%s%s%s" % (os.linesep, counter*indent, line)
                    open_flag = 0
                elif close:
                    counter -= 1
                    if open_flag:
                        pretty_xml += line
                    else:
                        pretty_xml += "%s%s%s" % (os.linesep, counter*indent, line)
                    open_flag = 0
                elif line.startswith('<![CDATA['):
                    pretty_xml += "%s%s%s" % (os.linesep, counter*indent, line)
                    open_flag = 0
                elif open_:
                    pretty_xml += "%s%s%s" % (os.linesep, counter*indent, line)
                    counter += 1
                    open_flag = 1
        else:
            pretty_xml += "%s%s" % (os.linesep, line)
    return pretty_xml.lstrip()

if __name__ == "__main__":
    import sys
    print prettify_xml(sys.stdin.read())
