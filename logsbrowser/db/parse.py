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

import re
from itertools import count
from string import Template
import functions
from string import Template
from utils.colors import check_color, ColorError, c_to_string

sub_dict = {'LIKE': ['%', (('_', '.'), ('%', '.*'))],
            'GLOB': ['*', (('?', '.'), ('*', '.*'))],
            'MATCH': ['', (('*', '\w*'),)]}


def operator_to_regexp(op, val):
    trim, maps = sub_dict[op.upper()]
    val = val.strip(trim)
    escaped_val = re.escape(val)
    for ch, new_ch in maps:
        escaped_val = escaped_val.replace(r'\%s' % ch, new_ch)
    return escaped_val


class AutoLid(Exception):
    pass


class ManySources(Exception):
    pass


clause1 = re.compile(
    '(?i)(?P<field>log)\s+(?P<op>(like|regexp|match|glob|=))\s+(?P<val>\$quote\d+)\s+as\s+(?P<color>.+)')
clause2 = re.compile(
    '(?i)(?P<op>(icontains|contains|iregexp))\(\s*(?P<field>log)\s*,\s*(?P<val>\$quote\d+)\s*\)\s+as\s+(?P<color>.+)')


def log_color_clauses(clauses):
    clauses = [c.strip('{}') for c in clauses]
    for cl in clauses:
        c = clause1.match(cl)
        if c:
            yield (c.group('op'), c.group('val'), c.group('color'))
        else:
            c = clause2.match(cl)
            if c:
                yield (c.group('op'), c.group('val'), c.group('color'))


op_to_re = {'LIKE': lambda v: re.escape(v.decode('utf8').strip('%')).replace('\%s' % '%',
                                                                             '.*').replace('\%s' % '_', '.'),
            'GLOB': lambda v: re.escape(v.decode('utf8').strip('*')).replace('\%s' % '*',
                                                                             '.*').replace('\%s' % '?', '.'),
            'REGEXP': lambda v: v,
            'MATCH': lambda v: '(?i)'+re.escape(v.decode('utf8')).replace('\%s' % '*', '\w*'),
            'CONTAINS': lambda v: re.escape(v.decode('utf8')),
            'ICONTAINS': lambda v: '(?i)'+re.escape(v.decode('utf8')),
            'IREGEXP': lambda v: '(?i)'+v,
            }


def lw_hl_expr(lw_hl_clauses, quotes_dict):
    hls = []
    for op, val, color in lw_hl_clauses:
        val = Template(val).substitute(quotes_dict).strip("'")
        cval = op_to_re[op.upper()](val.strip())
        fcolor = c_to_string(color)
        hls.append('f%s,s#14b: %s' % (fcolor, cval))
    return '\n'.join(hls)


class Query(object):

    select_re = re.compile(r'(?i)\(\s*select\s')
    query_re = re.compile(r'\(\$query\d+\)')

    def __init__(self, sql, fts, is_child=False):
        self.qdict = {}
        self.sql = ""
        self.find_queries(sql, fts)
        if not is_child:
            self.query.add_main_color_column()

    def find_queries(self, query, fts):
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
                        self.qdict[query_n[1:]] = Query(
                            query[start+1:n], fts, True)
                        self.sql += query[lend:start] + '(' + query_n + ')'
                        lend = n+1
        if self.sql:
            self.sql += query[lend:]
        else:
            self.sql = query
        query_n = 'query0'
        self.qdict[query_n] = Select(self.sql, self, fts)
        self.sql = '$'+query_n

    @property
    def query(self):
        return self.qdict['query0']

    def __str__(self):
        query = self.sql
        for q in self.qdict:
            query = Template(query).safe_substitute(self.qdict)
        return query

    # def __repr__(self):
    #    return self.sql

    def get_colors(self):
        colors = []
        for k, v in self.qdict.iteritems():
            colors.extend(v.get_colors())
        return colors

    def get_from_table(self):
        def get_from(select_core, query):
            from_ = select_core.from_
            if len(from_) == 1:
                if self.query_re.match(from_[0]):
                    query_ = from_[0].strip('($)')
                    cores = query.qdict[query_].query.qdict
                    if len(cores) == 1:
                        return get_from(cores['mquery1'], query.qdict[query_])
                else:
                    return from_[0]
            else:
                return ""
        return get_from(self.query.qdict['mquery1'], self)

    def add_lid(self, group=False):
        from_queries = self.query.add_lid(group)
        for q in from_queries:
            query = self.qdict.get(q)
            if query:
                query.add_lid(group)


class Select:

    order_re = re.compile('(?i)order\s+by(.+?)(limit|$)')
    limit_re = re.compile('(?i)limit(.+?)')
    union_re = re.compile('(?i)(except|intersect|union|order|limit)')

    def __init__(self, expr, parent, fts, colorize=True):
        self.qdict = {}
        self.sql = ""
        self.find_queries(expr, colorize, fts)
        self.parse()
        self.parent = parent
        if colorize:
            self.add_colors()

    def find_queries(self, query, colorize, fts):
        query_count = count(1)
        queries = self.union_re.split(query)
        for q in queries:
            if 'select' in q.lower():
                query_n = '$mquery%d' % (next(query_count))
                self.qdict[query_n[1:]] = SelectCore(q, fts)
                self.sql += ' %s ' % query_n
            else:
                self.sql += q
        self.color_columns = []
        if colorize:
            for q in self.qdict.values():
                self.color_columns.extend(q.color_columns)
            if self.color_columns:
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

    # def __repr__(self):
    #    return self.sql

    def add_lid(self, group):
        from_queries = []
        for q in self.qdict:
            from_query = self.qdict[q].add_rows_for_log_window(group)
            if from_query:
                from_queries.append(from_query)
        return from_queries

    def from_queries(self):
        from_queries = {}
        for k, q in self.qdict.items():
            from_queries[k] = []
            for q_ in q.from_for_color:
                try:
                    from_queries[k].append(
                        self.select_from_parent(q_.strip('$()')))
                except KeyError:
                    pass
        return from_queries

    def select_from_parent(self, key):
        return self.parent.qdict[key].query

    def add_colors(self):
        for k, source_selects in self.from_queries().items():
            if len(source_selects) > 1:
                raise ManySources
            elif len(source_selects) > 0:
                from_select = source_selects[0]
            else:
                continue
            if from_select.colorized:
                self.qdict[k].add_colors(list(from_select.color_columns))
                self.color_columns = self.color_columns.union(
                    from_select.color_columns)

    def add_main_color_column(self):
        if self.colorized:
            for k, q in self.qdict.items():
                q.result_list.append("'#fff' as bgcolor")

    def get_colors(self):
        colors = []
        for k, v in self.qdict.iteritems():
            colors.extend(v.colors)
        return colors

    @property
    def colorized(self):
        return bool(self.color_columns)


class SelectCore:

    select_expr = re.compile(r'(?i)select(.+?)(from|$)')
    from_re = re.compile(r'(?i)from(.+?)(where|group\s+by|order\s+by|limit|$)')
    where_re = re.compile('(?i)where(.+?)(group\s+by|order\s+by|limit|$)')
    group_re = re.compile('(?i)group\s+by(.+?)(order\s+by|limit|$)')
    query_templ = re.compile('\$query\d+')
    color = re.compile(
        r'{(?P<clause>.+?)\s+as\s+(?P<color>([a-zA-z]+|#[A-Fa-f0-9]+))}')
    color_count = count(1)
    logic = re.compile('''(?i)\sand\s|\sor\s|\snot\s''')

    def __init__(self, expr, fts):
        self.fts = fts
        self.sql = expr
        self.colorized = False
        self.colors = []
        self.color_columns = []
        self.parse()
        self.right_query()

    def parse(self):
        results = self.select_expr.search(self.sql).group(1).strip()
        self.result_list = split(results)
        group = self.group_re.search(self.sql)
        if group:
            self.group = [g.strip() for g in group.group(1).split(',')]
        else:
            self.group = []
        from_ = self.from_re.search(self.sql)
        if from_:
            self.from_ = [f.strip() for f in from_.group(1).split(',')]
        else:
            self.from_ = []
        self.from_for_color = self.from_
        self.queries_for_autolid = [q.strip('$()') for q in self.from_ if
                                    self.query_templ.match(q.strip('()'))]
        self.result_list = [self.parse_color(c) for c in self.result_list]

        where = self.where_re.search(self.sql)
        if where:
            self.where = where.group(1)
        else:
            self.where = ''

    def is_agg(self):
        if self.group:
            return True
        else:
            agg_fs = [f+'(' for f in functions.aggregate_functions]
            for result in self.result_list:
                for af in agg_fs:
                    if result.startswith(af):
                        return True
            return False

    def add_rows_for_log_window(self, def_group):
        if self.from_:
            if len(self.from_) == 1:
                group = self.is_agg() or def_group
                if self.queries_for_autolid:
                    if group:
                        self.result_list.insert(0,
                                                'rows(rows_for_log_window) as rows_for_log_window')
                    else:
                        self.result_list.insert(0,
                                                'rows_for_log_window')
                    return self.queries_for_autolid[0]

                else:
                    if group:
                        self.result_list.insert(0,
                                                'rows(lid) as rows_for_log_window')
                    else:
                        self.result_list.insert(0,
                                                'lid as rows_for_log_window')
                    return None
            else:
                raise AutoLid("Cannot use auto_lid with several sources")

    def parse_color(self, column):
        color = self.color.match(column)
        if color:
            self.colors.append(color.group())
            clause = color.group('clause')
            if ' match ' in clause.lower() and self.fts:
                new_query = Query('select from %s where %s' %
                                  (', '.join(self.from_), clause), self.fts)
                new_query.add_lid(True)
                clause = 'intersct(%s, (%s))' % (
                    'rows_for_log_window' if self.queries_for_autolid
                    else 'lid',
                    str(new_query))
            self.colorized = True
            group = self.is_agg()
            bgcolor = 'bgcolor%d' % next(self.color_count)
            self.color_columns.append(bgcolor)
            color_value = color.group('color')
            if check_color(color_value):
                return (('color_agg(' if group else '') +
                        "(case when %s then '%s' else '#fff' end)" %
                        (clause, color_value) +
                        (')' if group else '') +
                        ' as %s' % bgcolor)
            else:
                raise ColorError("Unknown color: %s" % color_value)
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
        columns = [c for c in self.result_list if c and c not in colors]
        colors.sort(key=lambda c: c[-1])
        def op_fields(s, seq): return ('%s %s' %
                                       (s, ', '.join(seq)) if seq else '')
        select = op_fields('select', columns+colors)
        from_ = self.from_ and op_fields('from', self.from_)
        where = self.where and op_fields('where', [self.where])
        group = self.group and op_fields('group by', self.group)
        return ' '.join([select, from_ or '', where or '', group or ''])

    def right_query(self):
        if (self.fts and ' match ' in self.where.lower() and
                self.logic.search(self.where)):
            clauses, clauses_dict = cut_clauses(self.where)
            for name, clause in clauses_dict.iteritems():
                clauses_dict[name] = logic_to_sets(
                    clause, '', 'select * from %s' % ','.join(self.from_), self.fts)
            for name, clause in clauses_dict.iteritems():
                if name != 'clause0':
                    clauses_dict[name] = 'select * from (%s)' % clauses_dict[name]
            for i in clauses_dict:
                clauses = Template(clauses).safe_substitute(clauses_dict)
            self.where = ''
            self.from_ = ['(%s)' % clauses]

   # def __repr__(self):
   #     return self.sql


def reset_select_core_counter():
    SelectCore.color_count = count(1)


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
    new_query += query[lend:]
    return new_query, quotes_dict


def split(select):
    results = []
    cur_column = ""
    in_brackets = 0
    for c in select:
        if c == "," and not in_brackets:
            results.append(cur_column.strip())
            cur_column = ""
        else:
            cur_column += c
        if c == '(':
            in_brackets += 1
        elif c == ')':
            in_brackets -= 1
    results.append(cur_column.strip())
    return results


ss = re.compile('\s+')


def process(sql_t, context, autolid, fts):
    reset_select_core_counter()
    sql = Template(sql_t).safe_substitute(context)
    sql = ss.sub(' ', sql)
    sql_no_quotes, quotes_dict = cut_quotes(sql)
    query = Query(sql_no_quotes, fts)
    from_ = query.get_from_table()
    lw_hl_clauses = log_color_clauses(query.get_colors())
    if autolid:
        query.add_lid()
    query = Template(str(query)).safe_substitute(quotes_dict)
    words_hl = lw_hl_expr(lw_hl_clauses, quotes_dict)
    query = Template(str(query)).safe_substitute({'time':
                                                  "strftime('%H:%M:%f',date)"})
    return (query, words_hl, from_)


and_ = re.compile(r'(?i)\sand\s')
not_ = re.compile(r'(?i)\snot\s')
or_ = re.compile(r'(?i)\sor\s')
expr = re.compile(r'''(?i)\w+\s*(not\s+)?\w+\s*[a-zA-Z0-9_$.]+''')


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


def logic_to_sets(simple_clause, before_from, before_where, fts):
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
                    new_ands.append(
                        ' '.join([before_where, 'where', and_cl.strip()]))
                else:
                    new_ands.append(and_cl.strip())
        ands = ' intersect '.join(new_ands)
        new_ors.append(before_from + wrap(ands) if len(new_ands)
                       > 1 and len(ors) > 1 else ands)
    return ' union '.join(new_ors)


def not_clause(clause, before_from, before_where):
    return 'select * from (%s)' % " ".join([before_where, 'except', before_where, 'where '+not_.sub(' ',
                                                                                                    clause).strip()])


def wrap(expr):
    return "("+expr+")"


if __name__ == '__main__':
    pass
    # print process("select date, time, {log regexp 'abc' as #ff0} from this where log MATCH 'test' AND (log=123 OR log NOT LIKE 'abcd') group by date order by date desc")
    # print q
    # print 80*'_'
    # print process("select date, (select test from this where log MATCH 'test' or log MATCH 'abcd'), time from this group by date order by date desc")
    # print 80*'_'
    # print process("select date, time from this where log not match 'testc' and (log not MATCH 'testb' or log match 'testa') group by date order by date desc")
    # print q
    # import pdb
    # pdb.set_trace()
    # print process("select * from (select date, time from this where log NOT MATCH 'test') group by date order by date desc")
    # print q
    # print 80*'_'
    # print process("select date, time from this where log MATCH 'test' group by date")
    # print 80*'_'
    # print process("select date, {log REGEXP 'tes' as #fff}, time from this where log not MATCH 'test' group by date order by date")
    # print 80*'_'
    # print process("select date, {log REGEXP 'test' as #ff0} from this where log NOT MATCH 'test' union select * from this where log NOT MATCH 'testa' order by test")
    # print q
    # print process("select date, logname, type from s where exists (select * from asdasd,asada where log not match 'test') order by date desc")
    # print process('select date from (select date, {log regexp "testc" as #ff0} from this) where log match "test" and log match "test" group by date')

    # print process("""select min(date), max(date), logname, error(type)
# from (select date, logname, type, group_logname(logname) as logname_group, {log REGEXP 'test2' as #f00}
# from (select *, {log REGEXP 'test' as #ff0}, {log match 'test2' as #00f} from
# this where log not match 'test')
# group by date, logname, type
# order by date DESC)
# group by logname_group
# order by logname_group desc""")
    # print process('''select date from (select a,$color{log match 'test' as #ff0} from this union select a, $color{log match 'xaxaxa' as #fff} from

    # print process("select date, logname, type, {log MATCH 'SUCCESS' as #ff0} from _asacsaca")
