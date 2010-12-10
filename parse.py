from pyparsing import *

#sep = Literal(".") | Literal("_")
sep = Suppress(Literal("_") | Literal("-") | Literal("."))
date = Combine((Word(nums, exact=4) | Word(nums, exact=2))  + Optional(sep) +\
    Word(nums, exact=2) + Optional(sep) + Word(nums, exact=2))
time = Combine(Word(nums, exact=2)  + Optional(sep) +\
    Word(nums, exact=2) + Optional(sep) + Word(nums, exact=2))
hour = Word(nums, max=2)
counter = Literal(".")+Word(nums, max=2)("counter")
datetime = date + Optional(sep + hour | time+counter) # (hour | time))
ext = Literal(".")+Word(alphas, exact=3)("ext")+Optional(counter | sep+date)+LineEnd()
logname = SkipTo(date | sep+date | ext) #delimitedList(Word(alphanums),'.') | delimitedList(Word(alphanums), '_')
filename=Optional(datetime+sep)+logname("logname")+Optional(Optional(sep)+datetime)+Optional(logname)+ext#+ext
#filename = datetime+sep+logname+Optional(sep)+Optional(datetime)+sep+ext+Optional(sep+date+sep+counter)

print filename.parseString("ProcessorService.txt.2010-12-09")
print filename.parseString("InterfaceService.txt")
print filename.parseString("debug-all.log")
print filename.parseString("OrderCatalogue.BL.log.3")
print filename.parseString("FORIS.TelCRM.Interfaces.Workflow2.log")
print filename.parseString("20101210_09_RequestObject.w3wp.Log")
print filename.parseString("20101210_CRM.Gateway.Community.Log")
print filename.parseString("MoveNextFromWaitingService.exe.config.txt")
print filename.parseString("MoveNextFromWaitingService.exe.config.txt.1")
print filename.parseString("PerformanceLog_ChangeContractOwner_2010_12_10.log")
print filename.parseString("AccountsReceivable_2010-12-10_FinancialData.log")
print filename.parseString("FORIS.Billing.BillingEngine.BAS_10-12-10_BillingApplicationServerMainWorkItem.log")
print filename.parseString("FORIS.Billing.BillingEngine.BAS_10-12-10_System.ServiceProcess.ServiceBase.log")
print filename.parseString("wslog_10122010.log")
print filename.parseString("uprsg20101210.log")
#print filename.parseString("uprsg20101210.log20101210.log") #!
print filename.parseString("20101210_CTIManager_Message.log")
print filename.parseString("CounterFormatter20101209202233.27.txt")
#print filename.parseString("RatingEngine_2010-12-10-07-51-36.0563798.txt") #!
print filename.parseString("psp_20101210_11.log")
print filename.parseString("psp_timer_20101210_12.log")
print filename.parseString("4_3_0.000005.log")
#print filename.parseString("foris_catalogue_admin-101208.log") #!
#print filename.parseString("0122010000001-EMAILCON_EMAILCON_01_error.log") #nag-tc-05 MG
#nag-tc-06
