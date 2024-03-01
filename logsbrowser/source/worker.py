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

#! -*- coding: utf-8 -*-
from cleaner import clear
import os
from operator import itemgetter
import config
from parse import define_format
from utils.common import to_unicode, from_unicode
from collections import defaultdict

source_formats = defaultdict(dict)


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
                pfn = os.path.join(raw_key, "undefined")
            if ext in ('txt', 'log') and pfn in value:
                flf.append([fullf, pfn, source_formats[stand][raw_key, pfn]])
    return sorted(flf, key=itemgetter(1))


def lists_to_pathes(pathes):
    folders = {}
    dirs = set([p[0] for p in pathes])
    for dir_ in dirs:
        folders[dir_] = [p[1] for p in pathes if p[0] == dir_]
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
                # print "Not found format for file %s" % path
                return None
    except IOError:
        return None


def dir_walker(path, dir_callback, log_callback,  stand, parent=None):
    files = set()
    try:
        for f in os.listdir(path):
            fullf = os.path.join(path, f)
            f = to_unicode(f)
            fext = os.path.splitext(f)[1]
            ext_parent = fullf
            if fext:
                name, ext = clear(f)
                if ext in ('txt', 'log'):
                    if not name:
                        name = os.path.join(path, "undefined")
                    if name not in files:
                        format_ = date_format(fullf)
                        if format_:
                            if (path, name) not in source_formats[stand]:
                                source_formats[stand][(path, name)] = format_
                            log_callback(name, parent, ext_parent)
                            files.add(name)
                elif ext != 'mdb':
                    if os.path.isdir(fullf):
                        node = dir_callback(f, parent, ext_parent, True)
                        dir_walker(fullf, dir_callback,
                                   log_callback, stand, node)
            else:
                node = dir_callback(f, parent, ext_parent, True)
                dir_walker(fullf, dir_callback, log_callback, stand, node)
    except OSError:
        pass
