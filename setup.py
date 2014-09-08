#!/usr/bin/env python
import sys
import os
import platform
from setuptools import setup, find_packages, Extension


version = __import__('unicodecsv').__version__

if platform.python_implementation() == "CPython":
    try:
        from Cython.Build import cythonize
        extensions = cythonize(Extension('unicodecsv._cimpl',
                                         ['unicodecsv/_cimpl.pyx']))
    except ImportError:
        print >>sys.stderr, "unable to import Cython, building C extension from C source"
        extensions = [Extension('unicodecsv._cimpl',
                                ['unicodecsv/_cimpl.c'])]
else:
    extensions = []

setup(
    name='cunicodecsv',
    version=version,
    description="Python2's stdlib csv module is nice, but it doesn't support unicode. This module is a drop-in replacement which *does*.",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r').read(),
    author='Simon Percivall',
    author_email='percivall@gmail.com',
    url='https://github.com/simonpercivall/cunicodecsv',
    packages=find_packages(),
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

