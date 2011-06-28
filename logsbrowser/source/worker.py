#! -*- coding: utf-8 -*-
from cleaner import clear
import os
from operator import itemgetter
import config
from parse import define_format
from utils.common import to_unicode, from_unicode

source_formats = {}

def clear_source_formats(stand):
    if stand:
        source_formats[stand].clear()

def file_preparator(folders, stand):
    flf = []
    for key, value in folders.iteritems():
        raw_key = from_unicode(key)
        for file_ in os.listdir(raw_key):
            fullf = os.path.join(raw_key, file_)
            pfn, ext = clear(file_)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt', 'log') and pfn in value:
                flf.append([fullf, pfn, source_formats[stand][raw_key, pfn]])
    return sorted(flf, key=itemgetter(1))

def lists_to_pathes(lists):
    pathes = []
    for i in lists:
        pathes.append([os.sep.join(reversed(i[1:])), i[0]])
    folders = {}
    dirs = set([p[0] for p in pathes])
    for dir_ in dirs:
        folders[dir_] = [p[1] for p in pathes if p[0]==dir_]
    return folders

def pathes(lst, stand):
    return file_preparator(lists_to_pathes(lst), stand)

def join_path(prefix, path):
    return "%s%s" % (prefix, "|"+path if path else "")

def date_format(path):
    try:
        with open(path) as file_:
            pfunc = True
            for n, line in enumerate(file_):
                if n < config.MAX_LINES_FOR_DETECT_FORMAT:
                    pformat, pfunc, need_date = define_format(line)
                    if pformat:
                        return (pformat, pfunc, need_date)
                else:
                    break
            if not pfunc:
                print "Not found format for file %s" % path
                return None
    except IOError:
        return None

def dir_walker(path, dir_callback, log_callback, parent=None, prefix=""):
    source_formats.setdefault(prefix, {})
    files = set()
    try:
        for f in os.listdir(path):
            fullf = os.path.join(path, f)
            f = to_unicode(f)
            fext = os.path.splitext(f)[1]
            ext_parent = join_path(prefix, fullf)
            if fext:
                name, ext = clear(f)
                if ext in ('txt', 'log'):
                    if not name:
                        name = "undefined"
                    if name not in files:
                        format_ = date_format(fullf)
                        if format_:
                            if (path, name) not in source_formats[prefix]:
                                source_formats[prefix][(path, name)] = format_
                            log_callback(name, parent, ext_parent)
                            files.add(name)
                elif ext != 'mdb':
                    if os.path.isdir(fullf):
                        node = dir_callback(f, parent, ext_parent)
                        dir_walker(fullf, dir_callback, log_callback, node, prefix)
            else:
                node = dir_callback(f, parent, ext_parent)
                dir_walker(fullf, dir_callback, log_callback, node, prefix)
    except OSError:
        pass
