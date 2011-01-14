import unittest
from test_log_names import log_names
from parse import parse_filename

class TestParseFileName(unittest.TestCase):

    def check(self, parsed, true, full):
        self.assertEqual(parsed, true, "%s parsed incorrectly: %s instead of %s" % (full,parsed,true))


if __name__ == '__main__':
    for val in log_names:
        parsed, ext = parse_filename(val[0])
        def ch(p, s, l):
            return lambda self: self.check(p, s, l)
        setattr(TestParseFileName, "test_%s" % val[0], ch(parsed,val[1],val[0]))
    unittest.main()
