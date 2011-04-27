from string import Template
import re
from db import parse

class CTemplate(Template):
    def __init__(self, template):
        Template.__init__(self, template)

    def safe_substitute(self, mapping, **kws):
        parse.reset_select_core_counter()
        return parse.process(Template.safe_substitute(self, mapping, **kws))

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




    

        


        
