from pyparsing import *
from datetime import datetime, timedelta
import pdb



def parse_date(d):
    try:
        dformat = datetime.strptime(d[0], "%Y%m%d")
    except ValueError:
        try:
            dformat = datetime.strptime(d[0], "%y%m%d")
        except:
            dformat = datetime.strptime(d[0], "%d%m%Y")
    return dformat

def hour_to_date(d):
    if d.get('hour', 0):
        return d['date']+timedelta(int(d['hour'])/24.)
    elif d.get('time', 0):
        t=datetime.strptime(d['time'], "%H%M%S")
        return d['date']+timedelta(t.hour/24.+t.minute/(24.*60)+t.second/(24.*60*60))
    else:
        return d['date']

sep = Suppress(Literal("_") | Literal("-") | Literal("."))
date_with_full_year = (Word( nums, exact=4)  + Optional(sep) +\
    Word(nums, exact=2) + Optional(sep) + Word(nums, exact=2))
date_with_short_year = (Word(nums, exact=2)  + Optional(sep) +\
    Word(nums, exact=2) + Optional(sep) + Word(nums, exact=2))
date = Combine( date_with_full_year | date_with_short_year).setParseAction(parse_date)('date')
time = Suppress(Optional(sep))+Combine(Word(nums, exact=2)  + Optional(sep) +\
    Word(nums, exact=2) + Optional(sep) + Word(nums, exact=2) +\
    Suppress(Optional(sep)+Optional(Word(nums))))("time")
mgbeg = Word(nums,exact=13)
hour = Suppress(Optional(sep))+Word(nums, max=2)('hour')
counter = Literal(".")+Word(nums, max=2)("counter")
date_time = (Suppress(Optional(sep)) + date + Optional(time | hour)).setParseAction(hour_to_date)("datetime") # (hour | time))
ext = Optional(counter) + Suppress(Literal("."))+(Literal("txt") | Literal("log"))("ext")+Optional( counter | date_time )+LineEnd()
logname = SkipTo( date_time | ext) #delimitedList(Word(alphanums),'.') | delimitedList(Word(alphanums), '_')
filename=Optional(date_time+sep)+logname("logname")+Optional(date_time)+Optional(logname)("logname2")+Optional(Word(alphanums))+ext#+ext
#filename=logname("logname")+Literal("-")+Word(nums)+ext#+ext
#filename.setParseAction(lambda t: ''.join([t['logname'],t['logname2']]))
#filename = datetime+sep+logname+Optional(sep)+Optional(datetime)+sep+ext+Optional(sep+date+sep+counter)

#print filename.parseString("ProcessorService.txt.2010-12-09")
#print filename.parseString("InterfaceService.txt")
#print filename.parseString("debug-all.log")
#print filename.parseString("OrderCatalogue.BL.log.3")
#print filename.parseString("FORIS.TelCRM.Interfaces.Workflow2.log")
#print filename.parseString("20101210_09_RequestObject.w3wp.Log")
#print filename.parseString("20101210_CRM.Gateway.Community.Log")
#print filename.parseString("MoveNextFromWaitingService.exe.config.txt")
#print filename.parseString("MoveNextFromWaitingService.exe.config.txt.1")
#print filename.parseString("PerformanceLog_ChangeContractOwner_2010_12_10.log")
#print filename.parseString("AccountsReceivable_2010-12-10_FinancialData.log")
#print filename.parseString("FORIS.Billing.BillingEngine.BAS_10-12-10_BillingApplicationServerMainWorkItem.log")
#print filename.parseString("FORIS.Billing.BillingEngine.BAS_10-12-10_System.ServiceProcess.ServiceBase.log")
#print filename.parseString("wslog_10122010.log")
#print filename.parseString("uprsg20101210.log")
#print filename.parseString("uprsg20101210.log20101210.log") #!
#print filename.parseString("20101210_CTIManager_Message.log")
#print filename.parseString("CounterFormatter20101209202233.27.txt")
#print filename.parseString("RatingEngine_2010-12-10-07-51-36.0563798.txt") #!  check minutes seconds
#print filename.parseString("psp_20101210_11.log")
#print filename.parseString("psp_timer_20101210_12.log")
##print filename.parseString("4_3_0.000005.log") #???
#print filename.parseString("foris_catalogue_admin-101208.log") #! this is date??
#print filename.parseString("11122010000003-SMSCON_SMSCON_01_data.log") #nag-tc-05 MG

def to_date(d):
    return datetime(int(d['year']),
        int(d['month']),
        int(d['day']),
        int(d['hour']),
        int(d['min']),
        int(d['sec']),
        1000*int(d.get('ms', 0))
    )

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
               Word(nums, max=2)('sec')
#
msg=SkipTo(StringEnd())
file_log=StringStart()+Suppress(Optional(Level | Type))+date_format_2('datetime').setParseAction(to_date)+msg('msg')


