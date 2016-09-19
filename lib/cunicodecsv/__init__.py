import sys


if sys.version_info >= (3, 0):
    from csv import *
else:
    from .py2 import *


#http://semver.org/
__version__ = "1.3.2"
VERSION = __version__.split('.')
