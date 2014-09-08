# encoding: utf-8
# cython: embedsignature=True
import csv

from cpython cimport (
    Py_INCREF,
    PySequence_Check,
    PyList_CheckExact,
    PyTuple_CheckExact,
    PySequence_Length,
    PySequence_GetItem,
    PyList_New,
    PyList_GET_ITEM,
    PyList_SET_ITEM,
    PyTuple_GET_ITEM,
    PyUnicode_AsEncodedString,
    PyUnicode_FromEncodedObject,
)


cdef inline _stringify(s, const char * encoding, const char * errors):
    if s is None:
        return ''
    if isinstance(s, unicode):
        return PyUnicode_AsEncodedString(s, encoding, errors)
    elif isinstance(s, (int, float)):
        pass  # let csv.QUOTE_NONNUMERIC do its thing.
    elif not isinstance(s, str):
        s = str(s)
    return s


cdef inline _stringify_list(l, char * encoding, char * errors):
    cdef int len_ = PySequence_Length(l)
    cdef list newl = PyList_New(len_)
    cdef int is_list = PyList_CheckExact(l)
    cdef int is_tuple = PyTuple_CheckExact(l)

    try:
        for i in range(len_):
            if is_list:
                v = <object>PyList_GET_ITEM(l, i)
            elif is_tuple:
                v = <object>PyTuple_GET_ITEM(l, i)
            else:
                v = PySequence_GetItem(l, i)
            str_ = _stringify(v, encoding, errors)
            Py_INCREF(str_)
            PyList_SET_ITEM(newl, i, str_)
        return newl
    except TypeError as e:
        raise csv.Error(str(e))


cdef class UnicodeWriter(object):
    """
    >>> import unicodecsv
    >>> from cStringIO import StringIO
    >>> f = StringIO()
    >>> w = unicodecsv.writer(f, encoding='utf-8')
    >>> w.writerow((u'é', u'ñ'))
    >>> f.seek(0)
    >>> r = unicodecsv.reader(f, encoding='utf-8')
    >>> row = r.next()
    >>> row[0] == u'é'
    True
    >>> row[1] == u'ñ'
    True
    """
    cdef object writer
    cdef char * _encoding
    cdef char * _encoding_errors

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', errors='strict', *args, **kwds):
        self.writer = csv.writer(f, dialect, *args, **kwds)
        self._encoding = encoding
        if errors is None or errors == 'strict':
            self._encoding_errors = NULL
        else:
            self._encoding_errors = errors

    def writerow(self, row):
        if not PySequence_Check(row):
            raise csv.Error("sequence expected")
        self.writer.writerow(_stringify_list(row, self._encoding, self._encoding_errors))

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    @property
    def dialect(self):
        return self.writer.dialect

    @property
    def encoding(self):
        return self._encoding

    @property
    def encoding_errors(self):
        if self._encoding_errors == NULL:
            return 'strict'
        return self._encoding_errors



cdef class UnicodeReader(object):
    cdef object reader
    cdef public char * encoding
    cdef public char * encoding_errors

    def __init__(self, f, dialect=None, encoding='utf-8', errors='strict', **kwds):
        format_params = ['delimiter',
                         'doublequote',
                         'escapechar',
                         'lineterminator',
                         'quotechar',
                         'quoting',
                         'skipinitialspace']
        if dialect is None:
            if not any([kwd_name in format_params for kwd_name in kwds.keys()]):
                dialect = csv.excel
        self.reader = csv.reader(f, dialect, **kwds)
        self.encoding = encoding
        self.encoding_errors = errors

    def __next__(self):
        cdef list row = self.reader.next()
        return [value if isinstance(value, float) else
                PyUnicode_FromEncodedObject(value, self.encoding, self.encoding_errors)
                for value in row]

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num
