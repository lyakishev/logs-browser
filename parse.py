from pyparsing import *
from datetime import datetime, timedelta
import re


nums_in_filename = re.compile(r"_?\.?\d+_?-?")

def parse_filename(path):
    fnwonums = nums_in_filename.sub('', path)
    fnparts = fnwonums.split('.')
    return (".".join(fnparts[:-1]) , fnparts[-1].lower())

def to_date(d):
    return datetime(int(d['year']),int(d['month']),int(d['day']),int(d['hour']),int(d['min']),int(d['sec']),1000*int(d.get('ms', 0)))

sep = Literal(".") | Literal(",") | Literal("-") | Literal(":")
LPAREN = Literal("[")
RPAREN = Literal("]")
Level = LPAREN + Word(alphas) + RPAREN
Type = Word(alphas)
date_format_1 = Suppress(Optional(LPAREN))+Word(nums, exact=4)('year')+sep+\
           Word(nums,exact=2)('month')+sep+\
           Word(nums, exact=2)('day')+\
           Word(nums, max=2)('hour')+sep+\
           Word(nums, max=2)('min')+sep+\
           Word(nums, max=2)('sec')+\
           Optional(sep+Word(nums)('ms'))+Suppress(Optional(RPAREN))

date_format_2 = Word(nums,exact=2)('day')+sep+\
                Word(nums,exact=2)('month')+sep+\
                Word(nums, exact=4)('year')+\
               Word(nums, max=2)('hour')+sep+\
               Word(nums, max=2)('min')+sep+\
               Word(nums, max=2)('sec')+\
               Optional(sep+Word(nums)('ms'))
#
msg=SkipTo(StringEnd())
file_log=StringStart()+Suppress(Optional(Level | Type))+(date_format_1 | date_format_2)('datetime').setParseAction(to_date)+msg('msg')


