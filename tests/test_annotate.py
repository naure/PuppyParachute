#!/usr/bin/env python3
import unittest
import os
import sys
if __name__ == '__main__':
    sys.path.append('.')

from puppyparachute.tools import tracing
from puppyparachute.annotate import annotate


def f(x):
    def inner_f(y):
        id(x)
        return C()
    c = inner_f('Yyy')
    return c.method('X')

class C(object):
    def method(self, a):
        that = a
        self.attr = that

        def inner(what):
            that == what

        return inner('Aaa')


class Test(unittest.TestCase):

    def test_annotate(self):
        with tracing(trace_all=True) as store:
            f('Traced code')

        afile = '{}-traced.py'.format(__file__)
        rm(afile)
        annotate(store, __file__)
        self.assertTrue(os.path.exists(afile))
        print(open(afile).read())
        found_f = False
        found_inner = False
        found_method = False
        found_method_inner = False
        found_local_change = False
        polluted = False
        with open(afile) as fd:
            for line in fd:
                if "{'x': " + "'Traced code'}" in line:
                    found_f = True
                if "'y': " + "'Yyy'" in line:
                    found_inner = True
                if (
                    "'self': " + "'" in line and
                    "'a': " + "'X'" in line
                ):
                    found_method = True
                if "'what': " + "'Aaa'" in line:
                    found_method_inner = True
                if "'self': " + "'test_annotate.C {attr: X}'" in line:
                    found_local_change = True
                if "!!" + "python" in line:
                    polluted = True
        self.assertTrue(found_f)
        self.assertTrue(found_inner)
        self.assertTrue(found_method)
        self.assertTrue(found_method_inner)
        self.assertTrue(found_local_change)
        self.assertTrue(not polluted)
        rm(afile)


def rm(path):
    try:
        os.remove(path)
    except:
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
