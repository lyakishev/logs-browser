from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

version = '1.7.1'

includefiles = [('logsbrowser/config', 'config'),
                ('gtk_for_build/etc', 'etc'),
                ('gtk_for_build/lib', 'lib'),
                ('gtk_for_build/share', 'share')]

buildOptions = dict(
            compressed = True,
            optimize = 2,
            packages = ['logsbrowser'],
            path = sys.path+['logsbrowser/'],
            include_files = includefiles
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
