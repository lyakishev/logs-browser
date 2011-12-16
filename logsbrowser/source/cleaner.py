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

"""This module cleans file names from junk"""

import re
import os

_digits = re.compile(r"(?<=[a-zA-Z])_\d{1,2}_(?=[a-zA-Z])|(?<=[a-zA-Z])\d(?=[a-zA-Z._])|\s|[-A-Za-z._]")
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
