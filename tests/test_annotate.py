#!/usr/bin/env python3
import unittest
import os
import sys
if __name__ == '__main__':
    sys.path.append('.')

from puppyparachute.store import format_db, load_db
from puppyparachute.tools import tracing
from puppyparachute.annotate import annotate, deannotate


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

    def some_entry_point(self):
        ' Record a trace in a file '
        with tracing(trace_all=True) as fndb:
            f('Traced code')
        with open('some_entry_point.yml', 'w') as fd:
            fd.write(format_db(fndb))

    def test_annotate(self):

        # Run a trace
        with tracing(trace_all=True) as fndb:
            f('Traced code')
        # Dump it and load it back
        dump = format_db(fndb)
        store = load_db(dump)
        self.assertTrue(len(store), 5)

        afile = '{}-traced'.format(__file__)
        restored_file = '{}-restored'.format(__file__)
        rm(afile)
        rm(restored_file)

        # Annotated the function at the top of this very file
        annotate(store, __file__, afile)
        self.assertTrue(os.path.exists(afile))

        # Doing it again yields the same output
        ''' XXX Doesn't work because of different filenames
        with open(afile) as fd:
            saved_afile = fd.read()
        annotate(store, afile, afile)
        with open(afile) as fd:
            self.assertEqual(fd.read(), saved_afile)
        '''

        # Check the annotations
        n_annotations = 0
        found_f = False
        found_inner = False
        found_method = False
        found_method_inner = False
        found_local_change = False
        # Do not erase regular comments
        found_random_comment = False
        polluted = False
        with open(afile) as fd:
            for line in fd:
                if line.strip().startswith('#?'):
                    n_annotations += 1
                if "x=" + "Traced code" in line:
                    found_f = True
                if "y=" + "Yyy" in line:
                    found_inner = True
                if (
                    "self" + "=" in line and
                    "a=" + "X" in line
                ):
                    found_method = True
                if "what=" + "Aaa" in line:
                    found_method_inner = True
                if r"self=" in line and r".C {attr: X}" in line:
                    found_local_change = True
                if '# Do not' + ' erase regular comments' == line.strip():
                    found_random_comment = True
                if "!!" + "python" in line:
                    polluted = True
        self.assertTrue(found_f)
        self.assertTrue(found_inner)
        self.assertTrue(found_method)
        self.assertTrue(found_method_inner)
        self.assertTrue(found_local_change)
        self.assertTrue(found_random_comment)
        self.assertEqual(n_annotations, 4)
        self.assertTrue(not polluted)

        # Remove annotations from the file
        deannotate(afile, restored_file)
        # It must be identical to the original file
        with open(__file__) as f_orig, open(restored_file) as f_restored:
            restored = f_restored.read()
            self.assertTrue(not any(
                line.strip().startswith('#?')
                for line in restored.splitlines()
            ))
            self.assertEqual(f_orig.read(), restored)

        rm(afile)
        rm(restored_file)


def rm(path):
    try:
        os.remove(path)
    except:
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
