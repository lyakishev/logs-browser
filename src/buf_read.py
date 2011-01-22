import os
from collections import deque

def b_read(path, buf = 0x16000):
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
        yield lines[0]


# copyright 2004 Michael D. Stenner <mstenner@ece.arizona.edu>
# license: LGPL

class xreverse:
    def __init__(self, file_object, buf_size=1024*96):
        self.fo = fo = file_object
        fo.seek(0, 2)        # go to the end of the file
        self.pos = fo.tell() # where we are 
        self.buffer = ''     # data buffer
        #self.lbuf = deque()       # buffer for parsed lines
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
            if self.pos == 0: return self.buffer

        self.lbuf = deque(self.buffer.splitlines(True))
        self.buffer = self.lbuf.popleft()

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

                self.lbuf = deque((new + self.buffer).splitlines(True))
                self.buffer = self.lbuf.popleft()

                if self.lbuf: return self.lbuf.pop()
                elif self.pos == 0:
                    if self.done:
                        raise StopIteration
                    else:
                        self.done = 1
                        return self.buffer + '\n'

