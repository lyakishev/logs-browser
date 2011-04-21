from string import Template
import re
from db import parse
import pdb


class NestedColor(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CTemplate(Template):
    
    color = re.compile(r'\$color{(?P<clause>.+?)\s+as\s+(?P<color>#[A-Fa-f0-9]+)}')
    quotes = re.compile(r'''('|")(.+?)\1''')
    parens = re.compile(r'''\((.+?)\)''')
    groupby = re.compile(r'(?i)group\s+by')
    from_ = re.compile(r'(?i)from')

    def __init__(self, template):
        Template.__init__(self, template)

    def safe_substitute(self, mapping, **kws):
        template, parens = self.cut(self.template, self.parens, 1)
        template, quotes = self.cut(template, self.quotes, 2)
        groupby = self.is_groupby(template)
        lend = 0
        new_template = ''
        for m in self.color.finditer(self.to_from(template)):
            start = m.start()
            end = m.end()
            color = m.group('color')
            cstart = m.start('clause')
            cend = m.end('clause')
            new_template += (self.template[lend:start] +
                        ('color_agg(' if groupby else '') +
                        "(case when %s then '%s' end)" %
                                (self.template[cstart:cend], color) +
                        (')' if groupby else '') +
                        ' as bgcolor')
            lend = end
        new_template+=self.template[lend:]
        nested_color = self.color.search(new_template)
        if nested_color:
            raise NestedColor('May use $color{...} expression in top level select query only')
        else:
            self.template = new_template
            #pdb.set_trace()
            return parse.process(Template.safe_substitute(self, mapping, **kws))

    def cut(self, template, re_obj, group):
        groups = []
        for m in re_obj.finditer(self.template):
            start = m.start(group)
            end = m.end(group)
            groups.append((start,end))
            template = template[:start]+'_'*(end-start)+template[end:]
        return template, groups

    def is_groupby(self, template):
        return bool(self.groupby.search(template))

    def to_from(self, template):
        match = self.from_.search(template)
        if match:
            return template[:match.start()]
        else:
            return template

if __name__ == '__main__':
    t=CTemplate("select date, logname, type, $color{log REGEXP 'SUCCESS' as #f00} from $this")
    print t.safe_substitute({'this':'_dscasdc32d'})
    print
    print 80*'-'
    print


    t=CTemplate("""select date, logname, type, 
                   $color{log REGEXP 'SUCCESS' as #f00},
                   $color{type='ERROR' as #f00}
                   from $this""")
    print t.safe_substitute({'this':'_dscasdc32d'})
    print
    print 80*'-'
    print

    t=CTemplate("select date, logname, $color{logid in (select lid from $this where log match 'SUCCESS') as #f00} from $this")
    print t.safe_substitute({'this':'_dscasdc32d'})
    print
    print 80*'-'
    print

    t=CTemplate("select date, logname, type, $color{log REGEXP 'SUCCESS' as #f00} from $this group by date, logname, type")
    print t.safe_substitute({'this':'_dscasdc32d'})
    print
    print 80*'-'
    print

    t=CTemplate("""select date, logname, type, 
                   $color{log REGEXP 'SUCCESS' as #f00},
                   $color{type='ERROR' as #f00}
                   from $this group by date""")
    print t.safe_substitute({'this':'_dscasdc32d'})
    print
    print 80*'-'
    print

    t=CTemplate("""select date, logname, type, 
                   $color{log REGEXP 'SUCCESS' as #f00},
                   $color{type='ERROR' as #f00}
                   from $this
                   where $color{log LIKE 'SPA' as #f00}
                   """)
    print t.safe_substitute({'this':'_dscasdc32d'})
    print
    print 80*'-'
    print




    

        


        
