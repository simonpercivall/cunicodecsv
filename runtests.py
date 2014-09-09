import unittest2
import doctest

def get_suite():
    loader = unittest2.TestLoader()
    suite = loader.discover('cunicodecsv')
    suite.addTest(doctest.DocTestSuite('cunicodecsv'))

    return suite

if __name__ == '__main__':
    result = unittest2.TestResult()
    get_suite().run(result)
    for error in result.errors:
        print error
