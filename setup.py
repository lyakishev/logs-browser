from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

version = '2.1.1'
build_dir = "build/logsbrowser%s" % version

import fileinput

for n, line in enumerate(fileinput.input('logsbrowser/ui/logsviewer.py', inplace=1)):
    if line.startswith("VERSION = "):
        print "VERSION = '%s'" % version
    else:
        print line,


includefiles = [('logsbrowser/config', 'config'),
                ('docs', 'docs'),
                ('gtk_for_build/etc', 'etc'),
                ('gtk_for_build/lib', 'lib'),
                ('gtk_for_build/share', 'share')]

buildOptions = dict(
            compressed = True,
            optimize = 2,
            packages = ['logsbrowser'],
            path = sys.path+['logsbrowser/'],
            include_files = includefiles,
            excludes = ["Tkinter", "ttk"],
            build_exe = build_dir
            )

setup(name='logsbrowser',
      version=version,
      description="",
      long_description="""\
""",
      author='Andrey V. Lyakishev',
      author_email='lyakav@gmail.com',
      url='',
      license='',
      packages=['logsbrowser', 'logsbrowser.db',
                      'logsbrowser.lparser','logsbrowser.lparser.events',
                      'logsbrowser.lparser.files',
                      'logsbrowser.source',
                      'logsbrowser.ui', 'logsbrowser.utils'],
      requires=['sqlite3', 'hashlib'],
      options = dict(build_exe = buildOptions),
      executables=[Executable("logsbrowser/main.py",base=base,
                              targetName="logsbrowser.exe",
                                copyDependentFiles = True,
                              )]
      )


for n, line in enumerate(fileinput.input('logsbrowser/ui/logsviewer.py', inplace=1)):
    if line.startswith("VERSION = "):
        print "VERSION = 'DEV'"
    else:
        print line,

import shutil
shutil.copy("logsbrowser/LICENSE", "%s/LICENSE" % build_dir)
