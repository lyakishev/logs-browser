import re
from itertools import count
from string import Template
import functions
import pdb

from_ = re.compile(r'(?i)from(.+?)(where|group|order|limit|$)')
select = re.compile(r'(?i)\(\s*select\s')
select_expr = re.compile(r'(?i)select(.+?)(from|$)')
where = re.compile('(?i)where(.+?)(group|order|limit|$)')
and_ = re.compile(r'(?i)\sand\s')
not_ = re.compile(r'(?i)\snot\s')
or_ = re.compile(r'(?i)\sor\s')
expr = re.compile(r'''(?i)\w+\s*(not\s+)?\w+\s*[a-zA-Z0-9_$.]+''')
logic = re.compile('''(?i)\sand\s|\sor\s|\snot\s''')
ss = re.compile('\s+')
query_templ = re.compile('\$[a-z]*query\d+')
union = re.compile('(?i)(except|intersect|union)')

def is_agg(query):
    if ' group ' in query.lower():
        return True
    else:
        shows = select_expr.search(query).group(1).split(',')
        agg_fs = [f+'(' for f in functions.aggregate_functions]
        for show in shows:
            for af in agg_fs:
                if af in show:
                    return True
        return False

def process_from(query):
    from_match = from_.search(query)
    if from_match:
        from_source = from_match.group(1)
        from_pos = from_match.start()
        from_queries = [q.strip()[1:] for q in from_source.split(',') if query_templ.search(q)]
        group = is_agg(query)
        if query_templ.search(from_source):
            if group:
                new_query = '%s, %s %s' % (query[:from_pos],
                                      'rows(rows_for_log_window) as rows_for_log_window',
                                      query[from_pos:])
            else:
                new_query = '%s, %s %s' % (query[:from_pos],
                                      'rows_for_log_window',
                                      query[from_pos:])

        else:
            if group:
                new_query = '%s, %s %s' % (query[:from_pos],
                                      'rows(lid) as rows_for_log_window',
                                      query[from_pos:])
            else:
                new_query = '%s, %s %s' % (query[:from_pos],
                                      'lid as rows_for_log_window',
                                      query[from_pos:])
        return (new_query, from_queries)
    else:
        return (query, [])


def auto_lid(query):
    lquery, lquery_dict = cut_queries(query, 'l')
    queries_for_auto_lid = []
    for lname, lquery_ in lquery_dict.iteritems():
        lqueries = []
        for lq_ in union.split(lquery_):
            qu, qus = process_from(lq_)
            queries_for_auto_lid.extend(qus)
            lqueries.append(qu)
        lquery_dict[lname] = ' '.join(lqueries)
    for q in lquery_dict:
        lquery = Template(lquery).safe_substitute(lquery_dict)
    return (lquery, queries_for_auto_lid)



def process(sql):
    sql = ss.sub(' ', sql)
    sql_no_quotes, quotes_dict = cut_quotes(sql)
    query, query_dict = cut_queries(sql_no_quotes)
    queries_for_auto_lid = []
    for name, query_ in query_dict.iteritems():
        queries = []
        for q_ in union.split(query_):
            if 'select' in q_.lower():
                rquery =  right_select(q_)
                if name == 'query0' or name in queries_for_auto_lid:
                    rquery, qus  = auto_lid(rquery)
                    queries_for_auto_lid.extend(qus)
                queries.append(rquery)
            else:
                queries.append(q_)
        query_dict[name] = ' '.join(queries)
    for i in query_dict:
        query = Template(query).safe_substitute(query_dict)
    query = Template(query).safe_substitute(quotes_dict)
    return query


def cut_queries(query_, prefix=""):
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
                        query_n = '$%squery%d' % (prefix, query_count.next())
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

    query_n = '$%squery0' % prefix
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
    #print process("select date, time from this where log MATCH 'test' AND (log=123 OR log NOT LIKE 'abcd') group by date order by date desc")
    #print 80*'_'
    #print process("select date, (select test from this where log MATCH 'test' or log MATCH 'abcd'), time from this group by date order by date desc")
    #print 80*'_'
    #print process("select date, time from this where log NOT MATCH 'testb' union select date, time from this where log NOT MATCH 'testa'")
    print 80*'_'
    print process("select * from (select date, time from this where log NOT MATCH 'test') group by date)")
    print 80*'_'
    #print process("select date, time from this where log MATCH 'test' group by date")
    #print 80*'_'
    #print process("select date, time from this where log MATCH 'test' order by date")
    #print 80*'_'
    #print process("select * from this where log NOT MATCH 'test' union select * from this where log NOT MATCH 'testa' order by test")






