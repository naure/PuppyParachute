#!/usr/bin/env python3
import unittest
from puppyparachute.trace import trace
from puppyparachute.store import freeze_db, format_db, load_db


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


class Test(unittest.TestCase):

    def test_dump_and_load(self):
        fndb, ret = trace(main1, [], trace_all=True)
        self.assertEqual(len(fndb), main1_fn_count)

        store = freeze_db(fndb)
        dump = format_db(store)
        dump_direct = format_db(fndb)
        self.assertEqual(dump, dump_direct)

        loaded = load_db(dump)
        self.assertDictEqual(loaded, store)


if __name__ == '__main__':
    unittest.main()
