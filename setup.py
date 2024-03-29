import shutil
import fileinput
from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

version = '2.0'


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
    compressed=True,
    optimize=2,
    packages=['logsbrowser'],
    path=sys.path+['logsbrowser/'],
    include_files=includefiles,
    excludes=["Tkinter", "ttk"]
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
                'logsbrowser.lparser', 'logsbrowser.lparser.events',
                'logsbrowser.lparser.files',
                'logsbrowser.source',
                'logsbrowser.ui', 'logsbrowser.utils'],
      requires=['sqlite3', 'hashlib'],
      options=dict(build_exe=buildOptions),
      executables=[Executable("logsbrowser/main.py", base=base,
                              targetName="logsbrowser.exe",
                              copyDependentFiles=True,
                              )]
      )


for n, line in enumerate(fileinput.input('logsbrowser/ui/logsviewer.py', inplace=1)):
    if line.startswith("VERSION = "):
        print "VERSION = 'DEV'"
    else:
        print line,

shutil.copy("logsbrowser/LICENSE", "build/exe.win32-2.7/LICENSE")
