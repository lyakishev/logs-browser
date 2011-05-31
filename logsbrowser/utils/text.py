import sys
import os

def convert_line_ends(text):
    if sys.platform == 'win32':
        return text.replace('\n', os.linesep)
    return text
