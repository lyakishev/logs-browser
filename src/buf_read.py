# -*- coding: utf-8 -*-
import mmap


def mmap_read(path):
    with open(path, 'rb') as mapped_file:
        try:
            data = mmap.mmap(mapped_file.fileno(), 0, access=mmap.ACCESS_READ)
        except WindowsError:
            #print "mmap error: %s" % path
            return
        mf_size = end_pos = len(data)
        for i in xrange(mf_size-1, -1, -1):
            if data[i] == "\n":
                yield data[i+1:end_pos+1]
                end_pos = i
        yield data[0:end_pos+1]


def mmap_block_read(path, block_size=1850):
    with open(path, 'rb') as mapped_file:
        try:
            data = mmap.mmap(mapped_file.fileno(), 0, access=mmap.ACCESS_READ)
        except WindowsError:
            #print "mmap error: %s" % path
            return
        mf_size = end_pos = len(data)
        for i in xrange(mf_size-1-block_size, -1, -block_size):
            text_block = data[i:end_pos+1]
            ret_pos = text_block.find("\n")
            if ret_pos >= 0:
                for line in text_block.splitlines(True)[-1:0:-1]:
                    yield line
            else:
                ret_pos = 0
            end_pos = i + ret_pos
        text_block = data[0:end_pos+1]
        for line in text_block.splitlines(True)[::-1]:
            yield line
