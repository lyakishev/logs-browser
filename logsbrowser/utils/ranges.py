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
            yield form_clause(cl,prefix,1)
            cl = [curr]
            prev = curr
    yield form_clause(cl,prefix,3)

def ranges(values, prefix):
    ints = sorted(map(int, values.split(',')))
    for cl in chain.from_iterable(clause(ints, prefix)):
        yield cl

