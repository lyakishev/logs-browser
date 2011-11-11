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

import time

NON_PRINTABLE = "\x00"#.join(chr(i) for i in range(8))

def strip_non_printable(msg):
    return msg.translate(None, NON_PRINTABLE)
    
def isoformat(t):
    return time.strftime('%Y-%m-%d %H:%M:%S', t)

def to_unicode(msg):
    try:
        return msg.decode('utf-8')
    except UnicodeDecodeError:
        return msg.decode('cp1251', 'ignore')

def from_unicode(msg):
    try:
        return msg.encode('cp1251')
    except UnicodeEncodeError:
        return msg.encode('utf-8')

