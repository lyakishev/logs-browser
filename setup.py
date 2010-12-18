from distutils.core import setup
import py2exe

setup(
    name = 'Log-Viewer',
    description = 'Tool for collect logs',
    author='Lyakishev Andrey',
    version = '2.0',
    packages=['widgets'],

    windows = [
                  {
                      'script': 'logviewer.py',
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
                  }
              },
)

