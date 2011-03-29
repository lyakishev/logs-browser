"""This module cleans file names from junk"""

import re
import os

_digits = re.compile(r"(?<=[a-zA-Z])\d(?=[a-zA-Z._])|\s|[A-Za-z._-]")
_t = re.compile(r"(?<=\d)T(?=\d)")
_start_end_literals = re.compile("^[._-]+|[._-]+$")
_repeated_literals = re.compile(r"([._-]){2,}")
_repeated_extension = re.compile(r"(\.[a-zA-Z]{3})\1+")
_null = re.compile(r"(?<![A-Za-z])null(?![A-Za-z])")
#_long_extension = re.compile(r"[A-Za-z_]{7,}")

def clear(path):
    """Parse file name: remove digits, "junk" literals etc."""
    fname = _t.sub('', path)
    fname = "".join(_digits.findall(fname))
    fname = _repeated_extension.sub(r'\1', fname)
    fname = _start_end_literals.sub('', fname)
    name, ext = os.path.splitext("a." + fname)
    name = _start_end_literals.sub('', name[2:])
    name = _repeated_literals.sub(r'\1', name)
    name = _null.sub("", name)
    return (name, ext[1:].lower())
