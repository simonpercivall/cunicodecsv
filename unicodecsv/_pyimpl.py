# encoding: utf-8
import csv


def _stringify(s, encoding, errors):
    if s is None:
        return ''
    if isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif isinstance(s, (int , float)):
        pass  # let csv.QUOTE_NONNUMERIC do its thing.
    elif not isinstance(s, str):
        s = str(s)
    return s

def _stringify_list(l, encoding, errors='strict'):
    try:
        return [_stringify(s, encoding, errors) for s in iter(l)]
    except TypeError as e:
        raise csv.Error(str(e))


class UnicodeWriter(object):
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
    def __init__(self, f, dialect=csv.excel, encoding='utf-8', errors='strict', *args, **kwds):
        self.encoding = encoding
        self.writer = csv.writer(f, dialect, *args, **kwds)
        self.encoding_errors = errors

    def writerow(self, row):
        self.writer.writerow(_stringify_list(row, self.encoding, self.encoding_errors))

    def writerows(self, rows):
        for row in rows:
          self.writerow(row)

    @property
    def dialect(self):
        return self.writer.dialect


class UnicodeReader(object):
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

    def next(self):
        row = self.reader.next()
        encoding = self.encoding
        encoding_errors = self.encoding_errors
        float_ = float
        unicode_ = unicode
        return [value if isinstance(value, float_) else
                unicode_(value, encoding, encoding_errors) for value in row]

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num
