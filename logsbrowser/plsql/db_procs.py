import cx_Oracle
import re


class ProcAnalyzer():
    def __init__(self, proc_string, db):
        self.proc = proc_string
        self.db = db
        self.split()
        self.connect()
        self.check()
        self.proc_body()

    def connect(self):
        self.conn = cx_Oracle.connect(self.db)
        self.cur = self.conn.cursor()

    def split(self):
        self.package, self.proc_name = self.proc.split('.')

    def check(self):
        self.cur.execute("""select count(*) from user_objects where object_name
            like :pack""", pack=self.package)
        exist = self.cur.fetchall()[0][0]
        if not exist:
            #print "Package does not exist"
            return False
        else:
            return True

    def proc_body(self):
        self.cur.execute("""select text from user_source where
                            type='PACKAGE BODY' and name=:pack 
                            order by line""", pack=self.package)
        source = self.cur.fetchall()
        proc_source = []
        line_number = 0
        re_start = re.compile("(?i)\s*(create|create or replace)?\s*(function|procedure).+?%s" %
                        self.proc_name.lower())
        re_end = re.compile("end\s+%s;" % self.proc_name.lower())
        for n, l in enumerate(source):
            line = l[0]
            if line.startswith("--"):
                continue
            lower_line = line.lower()
            if re_start.match(lower_line):#self.proc_name.lower() in lower_line:
                proc_source.append(line)
                if "procedure" in lower_line:
                    self.type_ = "proc"
                elif "function" in lower_line:
                    self.type_ = "func"
                line_number = n+1
                break
        for l in source[line_number:]:
            line = l[0]
            proc_source.append(line)
            if re_end.search(line.lower()):
                break
        self.proc_source = "".join(proc_source)

    def call(self):
        if self.type_ == "proc":
            pass
            #cursor.callproc
        elif self.type_ == "func":
            pass
            #cursor.callfunc

#oracle ca

if __name__ == "__main__":
    pa = ProcAnalyzer("PKG_CRM.get_HLR_code",
                     "tf2_stock/stock@heine")
    #print pa.proc_source
