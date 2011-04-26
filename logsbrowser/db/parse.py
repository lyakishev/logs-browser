import re
from itertools import count
from string import Template
import pdb


class AutoLid(Exception): pass
class ManySources(Exception): pass

def trace(f):
    def wrapper(*args, **kwargs):
        print f.func_name, args, kwargs
        r = f(*args, **kwargs)
        return r
    return wrapper
    

class Query(object):

    select_re = re.compile(r'(?i)\(\s*select\s')

    def __init__(self, sql, is_child=False):
        self.qdict = {}
        self.sql = ""
        self.find_queries(sql)
        if not is_child:
            self.query.add_main_color_column()

    def find_queries(self, query):
        queries = [m.start() for m in self.select_re.finditer(query)]
        inquery = 0
        lend = 0
        query_count = count(1)
        for n, c in enumerate(query):
            if n in queries:
                if not inquery:
                    start = n
                inquery += 1
            elif inquery and c == '(':
                inquery += 1
            elif c == ')':
                if inquery:
                    inquery -= 1
                    if inquery == 0:
                        query_n = '$query%d' % (next(query_count))
                        self.qdict[query_n[1:]] = Query(query[start+1:n], True)
                        self.sql += query[lend:start] + '(' + query_n + ')'
                        lend = n+1
        if self.sql:
            self.sql += query[lend:]
        else:
            self.sql = query
        query_n = 'query0'
        self.qdict[query_n] = Select(self.sql, self)
        self.sql = '$'+query_n

    @property
    def query(self):
        return self.qdict['query0']

    def __str__(self):
        query = self.sql
        for q in self.qdict:
            query = Template(query).safe_substitute(self.qdict)
        return query

    #def __repr__(self):
    #    return self.sql

    def add_lid(self):
        from_queries = self.query.add_lid()
        for q in from_queries:
            self.qdict[q].add_lid()


class Select:

    order_re = re.compile('(?i)order\s+by(.+?)(limit|$)')
    limit_re = re.compile('(?i)limit(.+?)')
    union_re = re.compile('(?i)(except|intersect|union|order|limit)')

    def __init__(self, expr, parent):
        self.qdict = {}
        self.sql = ""
        self.colorized = False
        self.find_queries(expr)
        self.parse()
        self.parent = parent
        self.add_colors()


    def find_queries(self, query):
        query_count = count(1)
        queries = self.union_re.split(query)
        for q in queries:
            if 'select' in q.lower():
                query_n = '$mquery%d' % (next(query_count))
                self.qdict[query_n[1:]] = SelectCore(q)
                self.sql += ' %s ' % query_n
            else:
                self.sql += q
        self.color_columns = []
        for q in self.qdict.values():
            self.color_columns.extend(q.color_columns)
        if self.color_columns:
            self.colorized = True
            self.color_columns = set(self.color_columns)
            for q in self.qdict.values():
                q.colorized = True
                for c in self.color_columns:
                    if c not in q.color_columns:
                        q.result_list.append("'#fff' as %s" % c)
                        q.color_columns.append(c)
        else:
            self.color_columns = set()

    def parse(self):
        order = self.order_re.search(self.sql)
        if order:
            self.order = [o.strip() for o in order.group(1).split(',')]
        else:
            self.order = []
        limit = self.limit_re.search(self.sql)
        if limit:
            self.limit = [l.split() for l in limit.group(1).split(',')]
        else:
            self.limit = []

    def __str__(self):
        query = self.sql
        for q in self.qdict:
            query = Template(query).safe_substitute(self.qdict)
        return query

    #def __repr__(self):
    #    return self.sql

    def add_lid(self):
        from_queries = []
        for q in self.qdict:
            from_query = self.qdict[q].add_rows_for_log_window()
            if from_query:
                from_queries.append(from_query)
        return from_queries

    def from_queries(self):
        from_queries = {}
        for k,q in self.qdict.items():
            from_queries[k] = []
            for q_ in q.from_:
                try:
                    from_queries[k].append(self.select_from_parent(q_.strip('()')[1:]))
                except KeyError:
                    pass
        return from_queries

    def select_from_parent(self, key):
        return self.parent.qdict[key].query

    def add_colors(self):
        for k, source_selects in self.from_queries().items():
            if len(source_selects)>1:
                raise ManySources
            elif len(source_selects)>0:
                from_select = source_selects[0]
            else:
                continue
            if from_select.colorized:
                self.qdict[k].add_colors(list(from_select.color_columns))
                self.color_columns = self.color_columns.union(from_select.color_columns)

    def add_main_color_column(self):
        if self.colorized:
            for k,q in self.qdict.items():
                q.result_list.append("'#fff' as bgcolor")

class SelectCore:

    select_expr = re.compile(r'(?i)select(.+?)(from|$)')
    from_re = re.compile(r'(?i)from(.+?)(where|group\s+by|order\s+by|limit|$)')
    where_re = re.compile('(?i)where(.+?)(group\s+by|order\s+by|limit|$)')
    group_re = re.compile('(?i)group\s+by(.+?)(order\s+by|limit|$)')
    query_templ = re.compile('\$query\d+')
    color = re.compile(r'{(?P<clause>.+?)\s+as\s+(?P<color>#[A-Fa-f0-9]+)}')
    color_count = count(1)
    logic = re.compile('''(?i)\sand\s|\sor\s|\snot\s''')

    def __init__(self, expr):
        self.sql = expr
        self.colorized = False
        self.color_columns = []
        self.parse()
        self.right_query()
        
    def parse(self):
        group = self.group_re.search(self.sql)
        if group:
            self.group = [g.strip() for g in group.group(1).split(',')]
        else:
            self.group = []
        results = self.select_expr.search(self.sql).group(1)
        self.result_list = [self.parse_color(c.strip()) for c in results.split(',')]
        from_ = self.from_re.search(self.sql)
        if from_:
            self.from_ = [f.strip() for f in from_.group(1).split(',')]
        else:
            self.from_ = []
        where = self.where_re.search(self.sql)
        if where:
            self.where =  where.group(1)
        else:
            self.where = ''

    def is_agg(self):
        if self.group:
            return True
        else:
            #agg_fs = [f+'(' for f in functions.aggregate_functions]
            #for result in results_list:
            #    for af in agg_fs:
            #        if af in result:
            #            return True
            return False

    def add_rows_for_log_window(self):
        if self.from_:
            if len(self.from_) == 1:
                group = self.is_agg()
                if self.query_templ.search(self.from_[0]):
                    if group:
                        self.result_list.insert(0,
                            'rows(rows_for_log_window) as rows_for_log_window')
                    else:
                        self.result_list.insert(0,
                                              'rows_for_log_window')
                    return self.from_[0].strip('()')[1:]

                else:
                    if group:
                        self.result_list.insert(0,
                                              'rows(lid) as rows_for_log_window')
                    else:
                        self.result_list.insert(0,
                                              'lid as rows_for_log_window')
                    return None
            else:
                raise AutoLid


    def parse_color(self, column):
        color = self.color.match(column)
        if color:
            self.colorized = True
            group = self.is_agg()
            bgcolor = 'bgcolor%d' % next(self.color_count)
            self.color_columns.append(bgcolor)
            return (('color_agg(' if group else '') +
                    "(case when %s then '%s' else '#fff' end)" %
                    (color.group('clause'), color.group('color')) +
                    (')' if group else '') +
                    ' as %s' % bgcolor)
        else:
            return column

    def add_colors(self, bgcolors):
        group = self.is_agg()
        self.colorized = True
        self.color_columns.extend(bgcolors)
        if group:
            self.result_list = ['color_agg(%(c)s) as %(c)s' % {'c': b} for b in
                                    bgcolors] + self.result_list
        else:
            self.result_list = bgcolors + self.result_list


    def __str__(self):
        colors = [c for c in self.result_list if 'bgcolor' in c]
        columns = [c for c in self.result_list if c not in colors]
        colors.sort(key = lambda c: c[-1])
        op_fields = lambda s, seq: ('%s %s' % (s, ', '.join(seq)) if seq else '')
        select = op_fields('select', columns+colors)
        from_ = self.from_ and op_fields('from', self.from_)
        where = self.where and op_fields('where', [self.where])
        group = self.group and op_fields('group by', self.group)
        return ' '.join([select, from_ or '', where or '', group or ''])

    def right_query(self):
        if ' match ' in self.where.lower() and self.logic.search(self.where):
            clauses, clauses_dict = cut_clauses(self.where)
            for name, clause in clauses_dict.iteritems():
                clauses_dict[name] = logic_to_sets(clause, '', 'select * from %s' % ','.join(self.from_))
            for name, clause in clauses_dict.iteritems():
                if name != 'clause0':
                    clauses_dict[name] = 'select * from (%s)' % clauses_dict[name]
            for i in clauses_dict:
                clauses = Template(clauses).safe_substitute(clauses_dict)
            self.where = ''
            self.from_ = ['(%s)' % clauses]

   # def __repr__(self):
   #     return self.sql
            
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

def process(sql):
    sql = ss.sub(' ', sql)
    sql_no_quotes, quotes_dict = cut_quotes(sql)
    query = Query(sql_no_quotes)
    query.add_lid()
    query = Template(str(query)).safe_substitute(quotes_dict)
    return query

and_ = re.compile(r'(?i)\sand\s')
not_ = re.compile(r'(?i)\snot\s')
or_ = re.compile(r'(?i)\sor\s')
expr = re.compile(r'''(?i)\w+\s*(not\s+)?\w+\s*[a-zA-Z0-9_$.]+''')
ss = re.compile('\s+')

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

def logic_to_sets(simple_clause, before_from, before_where):
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
                new_ands.append(not_clause(and_cl, before_from, before_where))
            else:
                if expr.match(and_cl.strip()):
                    new_ands.append(' '.join([before_where,'where',and_cl.strip()]))
                else:
                    new_ands.append(and_cl.strip())
        ands = ' intersect '.join(new_ands)
        new_ors.append(before_from + wrap(ands) if len(new_ands)>1 and len(ors)>1 else ands)
    return ' union '.join(new_ors)

def not_clause(clause, before_from, before_where):
    return 'select * from (%s)' %  " ".join([before_where,'except', before_where, 'where '+not_.sub(' ',
                clause).strip()])

def wrap(expr):
    return "("+expr+")"



if __name__ == '__main__':
    #print process("select date, time, {log regexp 'abc' as #ff0} from this where log MATCH 'test' AND (log=123 OR log NOT LIKE 'abcd') group by date order by date desc")
    ##print q
    #print 80*'_'
    #print process("select date, (select test from this where log MATCH 'test' or log MATCH 'abcd'), time from this group by date order by date desc")
    #print 80*'_'
    #print process("select date, time from this where log not match 'testc' and (log not MATCH 'testb' or log match 'testa') group by date order by date desc")
    ##print q
    ##import pdb
    ##pdb.set_trace()
    #print process("select * from (select date, time from this where log NOT MATCH 'test') group by date order by date desc")
    ##print q
    #print 80*'_'
    #print process("select date, time from this where log MATCH 'test' group by date")
    #print 80*'_'
    #print process("select date, {log REGEXP 'tes' as #fff}, time from this where log not MATCH 'test' group by date order by date")
    #print 80*'_'
    #print process("select date, {log REGEXP 'test' as #ff0} from this where log NOT MATCH 'test' union select * from this where log NOT MATCH 'testa' order by test")
    #print q
    #print process("select date, logname, type from s where exists (select * from asdasd,asada where log not match 'test') order by date desc")
    print process('select date, logname, type from this group by date, logname, type order by date desc')
    #import pdb
    #pdb.set_trace()
    print process("""select min(date), max(date), logname, error(type)
from (select date, logname, type, group_logname(logname) as logname_group, {log REGEXP 'test2' as #f00}
from (select *, {log REGEXP 'test' as #ff0}, {log match 'test2' as #00f} from
this where log not match 'test')
group by date, logname, type
order by date DESC)
group by logname_group
order by logname_group desc""")
    #print process('''select date from (select a,$color{log match 'test' as #ff0} from this union select a, $color{log match 'xaxaxa' as #fff} from
    #this) group by a''')
    #Query('select date, log, type from this where log match $quote1 AND log NOT match $quote2')





