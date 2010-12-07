from distutils.core import setup
import py2exe

setup(
    name = 'Log-Viewer',
    description = 'Tool for collect logs',
    version = '2.0',

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

