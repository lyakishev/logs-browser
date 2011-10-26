import pickle
import hashlib
import re


_keywords = re.compile("""(?i)(select|distinct|from|case|when|then|end|as|all|where|by|group|having|order|limit|offset|not|indexed|natural|left|outer|join|inner|cross|on|using|collate|asc|desc|union|all|intersect|except|cast|like|glob|regexp|match|escape|isnull|notnull|null|is|between|and|or|in|exists|else)""")
_space = re.compile("\s+")

_quoted = re.compile(r"""('|")(.+?)\1""")


def hash_value(params):
    pick = pickle.dumps(params)
    hash_v = hashlib.md5(pick).hexdigest()
    return "".join(["_",hash_v])

def _inqoutes(start, end, intervals):
    return any(map(lambda i: i[0]<start<end<i[1], intervals))

def sql_to_hash(sql):
    new_sql = ""
    quoted = [(m.start(2), m.end(2)) for m in _quoted.finditer(sql)]
    last_e = 0
    for m in _keywords.finditer(sql):
        s = m.start(0)
        e = m.end(0)
        new_sql += sql[last_e:s]
        if not _inqoutes(s, e, quoted):
            new_sql += sql[s:e].lower()
        else:
            new_sql += sql[s:e]
        last_e = e
    new_sql += sql[last_e:]
    sql_for_hash = ""
    last_end_quote = 0
    for start_quote, end_quote in quoted:
        sql_for_hash += _space.sub("", new_sql[last_end_quote:start_quote])
        sql_for_hash += new_sql[start_quote:end_quote]
        last_end_quote = end_quote
    sql_for_hash += _space.sub("", new_sql[last_end_quote:])
    return hashlib.md5(sql_for_hash).hexdigest()

    
