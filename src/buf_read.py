import os

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
        try:
            yield lines[0]
        except IndexError:
            return

