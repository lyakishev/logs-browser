import os
import re

filename_parser = re.compile("^(\d{8})?_?(\d{2})?_?(.+)\.(\d{4}.\d{2}.\d{2})?")

for i in range(1,2):
    for root, dirs, files in os.walk(r'\\msk-func-%0.2d\forislog' % i):
        for f in files:
            print filename_parser.search(f).group(3)
        #if filename_parser.search(f).group(1):
                          
                            #fo=file(os.path.join(root,f), 'r')
                            #fr=fo.read()
                            #if "VBScript" in fr:
                            #       print os.path.join(root,f)
                            #fo.close()

#os.path.getmtime(fname)))

