import pickle
import hashlib
import re


_keywords = re.compile("""(?i)(?<!['"])(select|distinct|from|case|when|then|end|as|all|where|by|group|having|order|limit|offset|not|indexed|natural|left|outer|join|inner|cross|on|using|collate|asc|desc|union|all|intersect|except|cast|like|glob|regexp|match|escape|isnull|notnull|null|is|between|and|or|in|exists|else)(?!['"])""")
_space = re.compile("\s+")


def hash_value(params):
    pick = pickle.dumps(params)
    hash_v = hashlib.md5(pick).hexdigest()
    return "".join(["_",hash_v])

def sql_to_hash(sql):
    lower_sql = _keywords.sub(lambda m: m.group().lower(), sql)
    sql_for_hash = _space.sub("", lower_sql)
    return hashlib.md5(sql_for_hash).hexdigest()

    
