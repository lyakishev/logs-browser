from cleaner import clear
import os
from operator import itemgetter

def file_preparator(folders):
    flf = []
    for key, value in folders.iteritems():
        for file_ in os.listdir(key):
            fullf = os.path.join(key, file_)
            pfn, ext = clear(file_)
            if not pfn:
                pfn = "undefined"
            if ext in ('txt', 'log') and pfn in value:
                flf.append([fullf, pfn])
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

def pathes(lst):
    return file_preparator(lists_to_pathes(lst))

def join_path(prefix, path):
    return "%s%s" % (prefix, "|"+path if path else "")

def dir_walker(path, dir_callback, log_callback, parent=None, prefix=""):
    files = set()
    try:
        for f in os.listdir(path):
            fext = os.path.splitext(f)[1]
            fullf = os.path.join(path, f)
            ext_parent = join_path(prefix, fullf)
            if fext:
                name, ext = clear(f)
                if ext in ('txt', 'log'):
                    if not name:
                        name = "undefined"
                    if name not in files:
                        log_callback(name, parent, ext_parent)
                        files.add(name)
                else:
                    if os.path.isdir(fullf):
                        node = dir_callback(f, parent, ext_parent)
                        dir_walker(fullf, dir_callback, log_callback, node, prefix)
            else:
                node = dir_callback(f, parent, ext_parent)
                dir_walker(fullf, dir_callback, log_callback, node, prefix)
    except OSError:
        pass
