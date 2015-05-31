# -*- coding: utf-8 -*-
import csv
try:
    from itertools import izip
except ImportError:
    izip = zip


pass_throughs = [
    'register_dialect',
    'unregister_dialect',
    'get_dialect',
    'list_dialects',
    'field_size_limit',
    'Dialect',
    'excel',
    'excel_tab',
    'Sniffer',
    'QUOTE_ALL',
    'QUOTE_MINIMAL',
    'QUOTE_NONNUMERIC',
    'QUOTE_NONE',
    'Error'
]
__all__ = [
    'reader',
    'writer',
    'DictReader',
    'DictWriter',
] + pass_throughs

for prop in pass_throughs:
    globals()[prop]=getattr(csv, prop)


def _unicodify(s, encoding):
    if s is None:
        return None
    if isinstance(s, (unicode, int, float)):
        return s
    elif isinstance(s, str):
        return s.decode(encoding)
    return s

try:
    from ._cimpl import UnicodeWriter, UnicodeReader, _stringify_list
except ImportError:
    from ._pyimpl import UnicodeWriter, UnicodeReader, _stringify_list
writer = UnicodeWriter
reader = UnicodeReader


class DictWriter(csv.DictWriter):
    """
    >>> from cStringIO import StringIO
    >>> f = StringIO()
    >>> w = DictWriter(f, ['a', u'ñ', 'b'], restval=u'î')
    >>> w.writerow({'a':'1', u'ñ':'2'})
    >>> w.writerow({'a':'1', u'ñ':'2', 'b':u'ø'})
    >>> w.writerow({'a':u'é', u'ñ':'2'})
    >>> f.seek(0)
    >>> r = DictReader(f, fieldnames=['a', u'ñ'], restkey='r')
    >>> r.next() == {'a': u'1', u'ñ':'2', 'r': [u'î']}
    True
    >>> r.next() == {'a': u'1', u'ñ':'2', 'r': [u'\xc3\xb8']}
    True
    >>> r.next() == {'a': u'\xc3\xa9', u'ñ':'2', 'r': [u'\xc3\xae']}
    True
    """
    def __init__(self, csvfile, fieldnames, restval='',
                 extrasaction='raise', dialect='excel', encoding='utf-8',
                 errors='strict', *args, **kwds):
        self.encoding = encoding
        csv.DictWriter.__init__(self, csvfile, fieldnames, restval, extrasaction, dialect, *args, **kwds)
        self.writer = UnicodeWriter(csvfile, dialect, encoding=encoding, errors=errors, *args, **kwds)
        self.encoding_errors = errors

    def writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        self.writerow(header)

class DictReader(csv.DictReader):
    """
    >>> from cStringIO import StringIO
    >>> f = StringIO()
    >>> w = DictWriter(f, fieldnames=['name', 'place'])
    >>> w.writerow({'name': 'Cary Grant', 'place': 'hollywood'})
    >>> w.writerow({'name': 'Nathan Brillstone', 'place': u'øLand'})
    >>> w.writerow({'name': u'Willam ø. Unicoder', 'place': u'éSpandland'})
    >>> f.seek(0)
    >>> r = DictReader(f, fieldnames=['name', 'place'])
    >>> print r.next() == {'name': 'Cary Grant', 'place': 'hollywood'}
    True
    >>> print r.next() == {'name': 'Nathan Brillstone', 'place': u'øLand'}
    True
    >>> print r.next() == {'name': u'Willam ø. Unicoder', 'place': u'éSpandland'}
    True
    """
    def __init__(self, csvfile, fieldnames=None, restkey=None, restval=None,
                 dialect='excel', encoding='utf-8', errors='strict', *args, **kwds):
        if fieldnames is not None:
            fieldnames = _stringify_list(fieldnames, encoding, errors)
        csv.DictReader.__init__(self, csvfile, fieldnames, restkey, restval,
                                dialect, *args, **kwds)
        self.reader = UnicodeReader(csvfile, dialect, encoding=encoding,
                                    errors=errors, *args, **kwds)
        if fieldnames is None and not hasattr(csv.DictReader, 'fieldnames'):
            # Python 2.5 fieldnames workaround.
            # See http://bugs.python.org/issue3436
            reader = UnicodeReader(csvfile, dialect, encoding=encoding,
                                   *args, **kwds)
            self.fieldnames = _stringify_list(reader.next(), reader.encoding, errors)

        if self.fieldnames is not None:
            self.unicode_fieldnames = [_unicodify(f, encoding) for f in
                                       self.fieldnames]
        else:
            self.unicode_fieldnames = []

        self.unicode_restkey = _unicodify(restkey, encoding)

    def next(self):
        row = csv.DictReader.next(self)
        result = dict((uni_key, row[str_key]) for (str_key, uni_key) in
                      izip(self.fieldnames, self.unicode_fieldnames))
        rest = row.get(self.restkey)
        if rest:
            result[self.unicode_restkey] = rest
        return result
