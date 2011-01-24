# -*- coding: utf-8 -*-
import os
from collections import deque
import mmap

###############################################################################
#this work wrong
def b_read(path, buf = 1024*96):
    with open(path,'r') as f:
        lines = ['']
        f.seek(0,2)
        size = f.tell()
        rem = size % buf
        pos = max(0, (size // buf - 1)*buf)
        while pos >= 0:
            f.seek(pos, os.SEEK_SET)
            data = f.read(rem+buf) + lines[0]
            rem = 0
            lines = data.splitlines(True)
            ix = len(lines) - 1
            while ix >= 1:
                yield lines[ix]
                ix -= 1
            pos -= buf
        try:
            yield lines[0]
        except:
            return
###############################################################################

# copyright 2004 Michael D. Stenner <mstenner@ece.arizona.edu>
# license: LGPL

class xreverse:
    def __init__(self, file_object, buf_size=1024*16):
        self.fo = fo = file_object
        fo.seek(0, 2)        # go to the end of the file
        self.pos = fo.tell() # where we are 
        if self.pos == 0:
           raise StopIteration
        self.buffer = ''     # data buffer
        self.lbuf = deque()       # buffer for parsed lines
        self.done = 0        # we've read the last line
        self.jump = -1 * buf_size
        
        while 1:
            try:            fo.seek(self.jump, 1)
            except IOError: fo.seek(0)
            new_position = fo.tell()
            new = fo.read(self.pos - new_position)
            fo.seek(new_position)
            self.pos = new_position

            self.buffer = new + self.buffer
            if '\n' in new: break
            if self.pos == 0:
                return

        nl = self.buffer.split('\n')
        nlb = [ i + '\n' for i in nl[1:-1] ]
        if not self.buffer[-1] == '\n': nlb.append(nl[-1])
        self.buffer = nl[0]
        self.lbuf = deque(nlb)

    def __iter__(self): return self

    def next(self):
        try:
            return self.lbuf.pop()
        except IndexError:
            fo = self.fo
            while 1:
                #get the next chunk of data
                try:            fo.seek(self.jump, 1)
                except IOError: fo.seek(0)
                new_position = fo.tell()
                new = fo.read(self.pos - new_position)
                fo.seek(new_position)
                self.pos = new_position

                nl = (new + self.buffer).split('\n')
                self.buffer = nl.pop(0)
                self.lbuf = deque([ i + '\n' for i in nl ])

                if self.lbuf: return self.lbuf.pop()
                elif self.pos == 0:
                    if self.done:
                        raise StopIteration
                    else:
                        self.done = 1
                        return self.buffer + '\n'

def mmap_read(path):
    with open(path, 'rb') as f:
        data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        n = len(data)
        for c in reversed(xrange(len(data))):
            if c == "\n":
                yield data[i+1:n]
                n=i
        yield data[0:n]


