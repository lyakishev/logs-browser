import unittest
from test_log_names import log_names
import sys
#sys.path.append(r"D:\log-viewer\src")
sys.path.append("/media/18BD-95C2/log-viewer/src")
import parse


class TestParseFileName(unittest.TestCase):

    def check(self, parsed, true, ext):
        self.assertEqual((parsed, ext), (true[1], true[2]), "%s parsed incorrectly: %s %s instead of %s %s" % (true[0],parsed,ext,true[1],true[2]))


if __name__ == '__main__':
    for val in log_names:
        parsed, ext = parse.parse_filename(val[0])
        def ch(p, v, e):
            return lambda self: self.check(p, v, e)
        setattr(TestParseFileName, "test_%s" % val[0], ch(parsed, val, ext))
    unittest.main()
