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
                lines = data[i:end_pos+1].splitlines(True)
                for line in lines[-1:0:-1]:
                    yield line
                ret_pos = len(lines[0]) - 1
                end_pos = i + ret_pos
            for line in data[0:end_pos+1].splitlines(True)[::-1]:
                yield line
    except (WindowsError, MemoryError, ValueError):
        for line in seek_block_read(file_, block_size):
            yield line



def mmap_block_read2(file_, block_size=8192):
    try:
        with closing(mmap.mmap(file_.fileno(), 0,
                     access=mmap.ACCESS_READ)) as data:
            mf_size = end_pos = end_msg_pos = start_msg_pos = len(data)
            for i in xrange(mf_size-1-block_size, -1, -block_size):
                lines = data[i:end_pos+1].splitlines(True)
                for line in lines[-1:0:-1]:
                    get_msg = (yield line)
                    start_msg_pos -= len(line)
                    if get_msg == 1:
                        yield (data[start_msg_pos:end_msg_pos],
                                end_msg_pos - start_msg_pos)
                        end_msg_pos = start_msg_pos
                    elif get_msg == 0:
                        end_msg_pos = start_msg_pos
                end_pos = i + len(lines[0]) - 1
            for line in data[0:end_pos+1].splitlines(True)[::-1]:
                get_msg = (yield line)
                start_msg_pos -= len(line)
                if get_msg == 1:
                    yield (data[start_msg_pos:end_msg_pos],
                            end_msg_pos - start_msg_pos)
                    end_msg_pos = start_msg_pos
                elif get_msg == 0:
                    end_msg_pos = start_msg_pos
    except (WindowsError, MemoryError, ValueError):
        pass

def seek_block_read(file_, block_size=8192):
    file_.seek(0,2)
    mf_size = end_pos = file_.tell()
    if mf_size > 0:
        i = mf_size-1-block_size
        while i > 0:
            file_.seek(i, 0)
            text_block = file_.read(end_pos+1-i)
            ret_pos = text_block.find("\n")
            if ret_pos >= 0:
                for line in text_block.splitlines(True)[-1:0:-1]:
                    yield line
            else:
                ret_pos = 0
            end_pos = i + ret_pos
            i -= block_size
        file_.seek(0, 0)
        text_block = file_.read(end_pos+1)
        for line in text_block.splitlines(True)[::-1]:
            yield line
