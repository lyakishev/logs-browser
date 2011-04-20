import unittest
from parse import *
import re

ss = re.compile('\s+')
def clear(string):
    return ss.sub('', string.lower())

class TestParseSQL(unittest.TestCase):
    
    def test_select_all(self):
        sql = 'select * from $this'
        new_sql = 'select * from $this'
        self.assertEqual(clear(process(sql)), clear(new_sql))

    def test_sql2(self):
        sql = """select date, logname, type from $this
               where log REGEXP 'test' and type='ERROR'"""
        new_sql = """select date, logname, type from $this
               where log REGEXP 'test' and type='ERROR'"""
        self.assertEqual(clear(process(sql)), clear(new_sql))

    def test_sql3(self):
        sql = """select date, logname, type from $this
               where log REGEXP 'test' or type='ERROR'"""
        new_sql = """select date, logname, type from $this
               where log REGEXP 'test' or type='ERROR'"""
        self.assertEqual(clear(process(sql)), clear(new_sql))

    def test_sql4(self):
        sql = """select date, logname, type from $this
               where log REGEXP 'test' or type='ERROR' and logname LIKE 'Spa%'"""
        new_sql = """select date, logname, type from $this
               where log REGEXP 'test' or type='ERROR' and logname LIKE 'Spa%'"""
        self.assertEqual(clear(process(sql)), clear(new_sql))

    def test_sql5(self):
        sql = """select date, logname, type from $this
               where log MATCH 'test'"""
        new_sql = """select date, logname, type from $this
               where log MATCH 'test'"""
        self.assertEqual(clear(process(sql)), clear(new_sql))

    def test_sql6(self):
        sql = """select date, logname, type from $this
               where log MATCH 'test' AND log MATCH 'abcd'"""
        new_sql = """select * from (
                    select date, logname, type from $this where log MATCH
                    'test'
                    intersect
                    select date, logname, type from $this where log MATCH
                    'abcd')"""
        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql7(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and type MATCH 'ERROR'"""
#        new_sql = """select date, logname, type from $this
#               where $this MATCH 'log:test type:ERROR'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql7(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and type MATCH 'ERROR' and log MATCH 'abcd'"""
#        new_sql = """select date, logname, type from $this
#               where $this MATCH 'log:test type:ERROR log:abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql9(self):
#        sql = """select date, logname, type from $this
#               where log NOT MATCH 'test'"""
#        new_sql = """select date, logname, type from $this
#                   except
#                   select date, logname, type from $this
#                   where log MATCH 'test'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql99(self):
#        sql = """select date, logname, type from $this
#               where log NOT MATCH 'test'
#               group by date
#               order by date"""
#        new_sql = """select date, logname, type from $this
#                   group by date
#                   except
#                   select date, logname, type from $this
#                   where log MATCH 'test'
#                   group by date
#                   order by date"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#
#    def test_sql10(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and log NOT MATCH 'abcd'"""
#        new_sql = """select date, logname, type from $this
#                   where $this MATCH 'log:test log:-abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql5(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname NOT MATCH 'abcd'"""
#        new_sql = """select date, logname, type from $this
#                   where $this MATCH 'log:test logname:-abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql11(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' OR log MATCH 'abcd'"""
#        new_sql = """select date, logname, type from $this
#               where $this MATCH 'log:test OR log:abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql12(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and (log MATCH 'edfr' OR log MATCH 'abcd')"""
#        new_sql = """select date, logname, type from $this
#               where $this MATCH 'log:test log:'edfr' OR log:'abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql13(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and log MATCH 'edfr' OR log MATCH 'abcd'"""
#        new_sql = """select date, logname, type from $this
#               where $this MATCH 'log:test log:edfr'
#               union
#               select date, logname, type from $this
#               where $this 'log:abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql14(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname REGEXP 'SPA'"""
#        new_sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname REGEXP 'SPA'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql15(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname REGEXP 'SPA and log REGEXP 'abcd'"""
#        new_sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname REGEXP 'SPA and log REGEXP 'abcd'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql16(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname NOT REGEXP 'SPA'"""
#        new_sql = """select date, logname, type from $this
#               where log MATCH 'test' and logname NOT REGEXP 'SPA'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql17(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test' OR logname REGEXP 'SPA'"""
#        new_sql = """select date, logname, type from $this
#               where log MATCH 'test' 
#               union 
#               select date, logname, type from $this
#               where logname REGEXP 'SPA'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
#    def test_sql18(self):
#        sql = """select date, logname, type from $this
#               where log MATCH 'test'"""
#        new_sql = """select date, logname, type from $this
#               where log MATCH 'test'"""
#        self.assertEqual(clear(process(sql)), clear(new_sql))
#
if __name__ == '__main__':
    unittest.main()




