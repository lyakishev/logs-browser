from pyparsing import *
from datetime import datetime, timedelta
import re


nums_in_filename = re.compile(r"_?\.?\d+_?-?")

def parse_filename(path):
    fnwonums = nums_in_filename.sub('', path)
    fnparts = fnwonums.split('.')
    return (".".join(fnparts[:-1]) , fnparts[-1].lower())

def to_date(t):
    d=t[0]
    if d.get('year', None):
        return datetime(int(d['year']),int(d['month']),int(d['day']),int(d['hour']),int(d['min']),int(d['sec']),int(str(1000*int(d.get('ms', 0)))[:6]))
    else:
        #return ",".join([d['hour'], d['min'], d['sec'], d.get('ms', "0"))
        return (int(d['hour']), int(d['min']), int(d['sec']), int(d.get('ms', "0")[:6]))

sep = Literal(".") | Literal(",") | Literal("-") | Literal(":")
#sep = "[.,-:]"
LPAREN = Literal("[")
#LPAREN = "\["
RPAREN = Literal("]")
#LPAREN = "\]"
Level = LPAREN + Word(alphas) + RPAREN
#Level = LPAREN+"\w+"+RPAREN
Type = Word(alphas)
#Type = \w+
date_format_1 = Suppress(Optional(LPAREN))+Group(Word(nums, exact=4)('year')+sep+\
           Word(nums,exact=2)('month')+sep+\
           Word(nums, exact=2)('day')+\
           Word(nums, max=2)('hour')+sep+\
           Word(nums, max=2)('min')+sep+\
           Word(nums, max=2)('sec')+\
           Optional(sep+Word(nums)('ms')))+Suppress(Optional(RPAREN))
#date_format_1=LPAREN+"?"+\d{4}+sep+\d{2}+sep+\d{2}+sep...

date_format_2 = Suppress(Optional(LPAREN))+Group(Word(nums,exact=2)('day')+sep+\
                Word(nums,exact=2)('month')+sep+\
                Word(nums, exact=4)('year')+\
               Word(nums, max=2)('hour')+sep+\
               Word(nums, max=2)('min')+sep+\
               Word(nums, max=2)('sec')+\
               Optional(sep+Word(nums)('ms')))+Suppress(Optional(LPAREN))

time_format = Suppress(Optional(LPAREN))+Group(Word(nums, exact=2)('hour')+sep+\
               Word(nums, exact=2)('min')+sep+\
               Word(nums, exact=2)('sec')+\
               sep+Word(nums)('ms'))+Suppress(Optional(RPAREN))
#
msg=SkipTo(StringEnd())
file_log=StringStart()+Suppress(Optional(Level | Type))+(  date_format_1 | date_format_2 | time_format )('datetime').setParseAction(to_date)+msg('msg')

def parse_logline(line, cdate):
    try:
        parsed_line = file_log.parseString(line)
    except ParseException:
        return None
    else:
        dt = parsed_line[0]
        if type(dt) is datetime:
            return (dt, parsed_line['msg'])
        else:
            full_dt = datetime(cdate.tm_year, cdate.tm_mon, cdate.tm_mday, dt[0], dt[1], dt[2], dt[3])
            return (full_dt, parsed_line['msg'])


