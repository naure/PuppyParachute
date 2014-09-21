#!/usr/bin/env python3
import sys
import unittest
from puppyparachute.trace import trace
from puppyparachute.store import format_db
from puppyparachute.tools import diff_db


def main():
    z = 1

    def f(x):
        y = x + z
        return y

    class C(object):
        def __init__(self, a):
            self.a = a

        def inc(self):
            self.a += 1

    f(2)
    c = C(10)
    c.inc()

main1 = main
main1_fn_count = 5


global_var = 0

def main():
    global global_var
    z = 1

    def f(x):
        y = x + z + global_var
        return y

    class C(object):
        def __init__(self, a):
            self.a = a

        def inc(self):
            self.a += 2

    c = C(10)
    c.inc()

    f(2)
    f(2)
    global_var = 100
    f(2)
    z = 10
    f(2)

main2 = main
main2_fn_count = 5


def main():
    def f(s):
        raise ValueError(s)
    try:
        f('Catch this error')
    except:
        pass

main_exc = main
main_exc_fn_count = 2


class Test(unittest.TestCase):

    def test_dump(self):
        fndb1, ret = trace(main1, [], trace_all=True)
        dump1 = format_db(fndb1)
        print(dump1)
        self.assertEqual(len(fndb1), main1_fn_count)

    def test_exception(self):
        fndbe, ret = trace(main_exc, [], trace_all=True)
        dumpe = format_db(fndbe)
        print(dumpe)
        self.assertEqual(len(fndbe), main_exc_fn_count)
        self.assertTrue(any(
            'ValueError' in line and 'Catch this error' in line
            for line in dumpe.splitlines()))

    def test_main(self):
        fndb1, ret1 = trace(main1, [], trace_all=True)
        fndb2, ret2 = trace(main2, [], trace_all=True)

        print(diff_db(fndb1, fndb2))

        self.assertEqual(len(fndb1), main1_fn_count)
        self.assertEqual(len(fndb2), main2_fn_count)
        self.assertEqual(list(fndb1.keys()), list(fndb2.keys()))
        self.assertNotEqual(fndb1, fndb2)

    def test_settrace(self):
        previous = sys.gettrace()

        def nimp():
            return 'nimp'

        calls = []

        def logtrace(*args):
            calls.append(args)
        sys.settrace(logtrace)
        now = sys.gettrace()
        nimp()

        sys.settrace(previous)
        self.assertEqual(now, logtrace)
        self.assertTrue(calls)


if __name__ == '__main__':
    unittest.main()
