#!/usr/bin/env python
import sys
import os
import platform
import re
from setuptools import setup, find_packages, Extension


def read_version():
    with open(os.path.join('lib', 'cunicodecsv', '__init__.py')) as f:
        m = re.search(r'''__version__\s*=\s*['"]([^'"]*)['"]''', f.read())
        if m:
            return m.group(1)
        raise ValueError("couldn't find version")


if platform.python_implementation() == "CPython":
    try:
        from Cython.Build import cythonize
        extensions = cythonize(Extension('cunicodecsv._cimpl',
                                         ['lib/cunicodecsv/_cimpl.pyx']))
    except ImportError:
        print >>sys.stderr, "unable to import Cython, building C extension from C source"
        extensions = [Extension('cunicodecsv._cimpl',
                                ['lib/cunicodecsv/_cimpl.c'])]
else:
    extensions = []

setup(
    name='cunicodecsv',
    version=read_version(),
    description="Python2's stdlib csv module is nice, but it doesn't support unicode. This module is a drop-in replacement which *does*.",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r').read(),
    author='Simon Percivall',
    author_email='percivall@gmail.com',
    url='https://github.com/simonpercivall/cunicodecsv',
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    ext_modules=extensions,
    tests_require=['unittest2 >= 0.5.1', 'Cython >= 0.20.1'],
    test_suite='runtests.get_suite',
    license='BSD License',
    classifiers=['Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Natural Language :: English',
                'Programming Language :: Python :: 2.5',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: Implementation :: CPython',],
)

