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

from itertools import chain

def form_clause(seq, prefix, quant):
    if len(seq)>quant:
        return ["%s>=%s and %s<=%s" % (prefix,min(seq),prefix,max(seq))]
    else:
        return ["%s=%s" % (prefix,v) for v in seq]

def clause(iter_, prefix):
    prev = iter_[0]
    cl = [prev]
    for curr in iter_[1:]:
        if curr - prev == 1:
            cl.append(curr)
            prev = curr
        else:
            yield form_clause(cl,prefix,2)
            cl = [curr]
            prev = curr
    yield form_clause(cl,prefix,2)

def ranges(values, prefix):
    ints = sorted(map(int, values.split(',')))
    clauses = list(chain.from_iterable(clause(ints, prefix)))
    n = len(clauses)
    if n > 999:
        for i in range(n/500):
            yield ' OR '.join(clauses[i*500:(i+1)*500])
        yield ' OR '.join(clauses[(i+1)*500:])
    else:
        yield ' OR '.join(clauses)


