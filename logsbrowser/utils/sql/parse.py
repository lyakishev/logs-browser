import re
from itertools import count
from string import Template

select = re.compile(r'(?i)\(\s*select\s')
where = re.compile('(?i)where(.+?)(group|order|limit|$)')
and_ = re.compile(r'(?i)\sand\s')
not_ = re.compile(r'(?i)\snot\s')
or_ = re.compile(r'(?i)\sor\s')
expr = re.compile(r'''(?i)\w+\s*(not\s+)?\w+\s*[a-zA-Z0-9_$.]+''')
logic = re.compile('''(?i)\sand\s|\sor\s|\snot\s''')
ss = re.compile('\s+')

def process(sql):
    sql = ss.sub(' ', sql)
    sql_no_quotes, quotes_dict = cut_quotes(sql)
    if ' match ' not in sql_no_quotes.lower():
        return sql
    query, query_dict = cut_queries(sql_no_quotes)
    for name, query_ in query_dict.iteritems():
        query_dict[name] = right_select(query_)
    for i in query_dict:
        query = Template(query).safe_substitute(query_dict)
    query = Template(query).safe_substitute(quotes_dict)
    return query


def cut_queries(query_):
    query_count = count(1)
    queries_dict = {}
    queries = [m.start() for m in select.finditer(query_)]
    def walk(query, queries):
        inquery = 0
        new_query = ""
        lend = 0
        for n, c in enumerate(query):
            if n in queries:
                if not inquery:
                    start = n
                inquery += 1
            if c == ')':
                if inquery:
                    inquery -= 1
                    if inquery == 0:
                        query_n = '$query%d' % query_count.next()
                        queries_dict[query_n[1:]] = '('+walk(query[start+1:n],
                                                [q-start-1 for q in queries
                                                if start+1<q<n])+')'
                        new_query += query[lend:start] + query_n
                        lend = n+1
        if new_query:
            new_query += query[lend:]
            return new_query
        else:
            return query

    query_n = '$query0' 
    queries_dict[query_n[1:]] = walk(query_, queries)

    return query_n, queries_dict


def right_select(query):
    s = '(' if query[0]=='(' else ''
    e = ')' if query[-1]==')' else ''
    query = query.strip('()')
    where = find_where(query)
    if where:
        if ('match' not in where[0].lower() or
                    not logic.search(where[0])):
            return s+query+e
        else:
            return s+build_query(query, where)+e
    else:
        return s+query+e

def build_query(query, where):
    order = where[3]
    before_where, after_where = (query[:where[1]],
                                 query[where[2]:order])
    q_order = query[order:]
    clauses, clauses_dict = cut_clauses(where[0])
    for name, clause in clauses_dict.iteritems():
        clauses_dict[name] = logic_to_sets(clause, before_where.strip())
    for i in clauses_dict:
        clauses = Template(clauses).safe_substitute(clauses_dict)
    return "%s (%s) %s" % ('select * from', clauses, q_order)
    

def cut_clauses(clauses_):
    clause_count = count(1)
    clauses_dict = {}
    def walk(clauses):
        inparen = 0
        lend = 0
        new_clauses = ""
        for n, c in enumerate(clauses):
            if c == '(':
                if not inparen:
                    start = n
                inparen += 1
            if c == ')':
                inparen -= 1
                if inparen == 0:
                    clause_n = '$clause%d' % clause_count.next()
                    clauses_dict[clause_n[1:]] = walk(clauses[start+1:n])
                    new_clauses += (clauses[lend:start] +
                                    clause_n)
                    lend = n+1
        if new_clauses:
            new_clauses += clauses[lend:]
            return new_clauses
        else:
            return clauses
    clause_n = '$clause0' 
    clauses_dict[clause_n[1:]] = walk(clauses_)
    return clause_n, clauses_dict

def logic_to_sets(simple_clause, before_where):
    simple_clause = simple_clause.lower()
    if ' match ' not in simple_clause:
        return ' '.join([before_where, 'where', simple_clause])
    ors = or_.split(simple_clause)
    new_ors = []
    wo_or = ' OR '.join([_or for _or in ors if ' match ' not in _or and ' and '
                            not in _or and expr.match(_or)])
    if wo_or:
        new_ors.append(' '.join([before_where, 'where', wo_or.strip()]))
    for or_cl in [_or for _or in ors if _or not in wo_or]:
        ands = and_.split(or_cl)
        new_ands = []
        wo_and = ' AND '.join([_and for _and in ands if ' match ' not in _and
                                and expr.match(_and)])
        if wo_and:
            new_ands.append(' '.join([before_where, 'where', wo_and.strip()]))
        for and_cl in [_and for _and in ands if _and not in wo_and]:
            if not_.search(and_cl):
                new_ands.append(not_clause(and_cl, before_where))
            else:
                if expr.match(and_cl.strip()):
                    new_ands.append(' '.join([before_where,'where',and_cl.strip()]))
                else:
                    new_ands.append('select * from ('+and_cl.strip()+')')
        ands = ' intersect '.join(new_ands)
        new_ors.append('select * from ' + wrap(ands) if len(new_ands)>1 and len(ors)>1 else ands)
    return ' union '.join(new_ors)

def not_clause(clause, before_where):
    return 'select * from ' + " ".join(["("+before_where,'except', before_where, 'where '+not_.sub(' ',
                clause).strip()+")"])

def wrap(expr):
    return "("+expr+")"


def find_where(query):
    clause = where.search(query)
    if clause:
        return clause.group(1), clause.start(0), clause.end(0), clause.start(2)
    else:
        return None


def find_order(query):
    order_ = order.search(query)
    if order_:
        return order_.start()
    return len(query)


def cut_quotes(query):
    qoutes_count = count(1)
    quotes = re.compile(r'''('|")(.+?)\1''')
    quotes_dict = {}
    new_query = ""
    lend = 0
    for m in quotes.finditer(query):
        start = m.start()
        end = m.end()
        quote_n = '$quote%d' % qoutes_count.next()
        quotes_dict[quote_n[1:]] = m.group()
        new_query += (query[lend:start] + quote_n)
        lend = end
    new_query+=query[lend:]
    return new_query, quotes_dict


if __name__ == '__main__':
    print process("select date, time from this where log MATCH 'test' AND (log=123 OR log NOT LIKE 'abcd') group by date order by date desc")
    print 80*'_'
    print process("select date, (select test from this where log MATCH 'test' or log MATCH 'abcd'), time from this group by date order by date desc")
    print 80*'_'
    print process("select date, time from this where log NOT MATCH 'test' AND log REGEXP 'test1' OR log NOT LIKE 'test2' AND log MATCH 'test3' group by date order by date desc")
    print 80*'_'
    print process("select date, time from this where log MATCH 'test'")


