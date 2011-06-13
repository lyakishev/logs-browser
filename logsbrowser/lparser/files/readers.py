# -*- coding: utf-8 -*-
import mmap
from contextlib import closing
import os

def mmap_block_read(file_, block_size=8192):
    try:
        with closing(mmap.mmap(file_.fileno(), 0,
                     access=mmap.ACCESS_READ)) as data:
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
    except (WindowsError, MemoryError, ValueError):
        for line in seek_block_read(file_, block_size):
            yield line

def seek_block_read(file_, block_size=8192):
    mf_size = end_pos = size
    for i in xrange(mf_size-1-block_size, -1, -block_size):
        file_.seek(i, 0)
        text_block = file_.read(end_pos+1-i)
        ret_pos = text_block.find("\n")
        if ret_pos >= 0:
            for line in text_block.splitlines(True)[-1:0:-1]:
                yield line
        else:
            ret_pos = 0
        end_pos = i + ret_pos
    file_.seek(0, 0)
    text_block = file_.read(end_pos+1)
    for line in text_block.splitlines(True)[::-1]:
        yield line
