import os
import pygtk
pygtk.require("2.0")
import gtk, gobject, gio
import re
from itertools import ifilter
from parse import filename

wndw = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
swndw=gtk.ScrolledWindow()
treestore = gtk.TreeStore( gobject.TYPE_STRING, gobject.TYPE_STRING )

parents={}
fls={}
for i in range(1,13):
    server_name = r'\\nag-tc-%0.2d\forislog' % i
    server = treestore.append(None, [server_name, ""])
    for root, dirs, files in os.walk(server_name):
        for subdir in dirs:
            parents[os.path.join(root, subdir)] = treestore.append(parents.get(root, server), [subdir,""])
        for item in files:
            name = filename.parseString(item)['logname']
            if not fls.get(name, None):
                treestore.append(parents.get(root, server), [name, item])
                fls[name]=item


view = gtk.TreeView(treestore)
renderer = gtk.CellRendererText()
renderer.set_property( 'editable', True )
column0 = gtk.TreeViewColumn("Log", renderer, text=0)
view.append_column( column0 )
renderer1 = gtk.CellRendererText()
renderer1.set_property( 'editable', True )
column1 = gtk.TreeViewColumn("File", renderer1, text=1)
view.append_column( column1 )
swndw.add(view)
wndw.add(swndw)
wndw.show_all()
gtk.main()


#def parse_logs(filename):
#    f=open(fillename, 'r')
#    s=f.read()
#    log = {}
#    for l in izip(testp.finditer(s), ifilter(lambda x: x, testp.split(s))):
#        yield {'the_time': l[0],
#                'msg': l[1],
#                'logtype': "",
#                'source' : "",
#                'computer' : ""
#        }
#
#
#if date_of_change < start_date:
#    pass
#elif date_from_filename < start_date:
#    pass
#else:
#    process


#filename_parser =re.compile(r"^(\d{8})?_?(\d{2})?_?(\w+\.(?!\d{2})+)(\d{4}.?\d{2}.?\d{2})?(\d{2}.?\d{2}.?\d{2})?.?([a-zA-Z]*).?(\d*).?([a-zA-Z]*)")
#re.split('[._-]?', "test")


                #print f, " ", mg_parser.search(f).group(2)
                #flss.append(mg_parser.search(f).group(2))
            #print f, "  ", filename_parser.search(f).group(3)
        #if filename_parser.search(f).group(1):
                            #fo=file(os.path.join(root,f), 'r')
                            #fr=fo.read()
                            #if "VBScript" in fr:
                            #       print os.path.join(root,f)
                            #fo.close()
#   sflss=set(flss)
 #   flens.append(len(sflss))
#print flens
#os.path.getmtime(fname)))


