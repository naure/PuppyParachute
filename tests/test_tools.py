#!/usr/bin/env python3
import unittest
import os
import sys
if __name__ == '__main__':
    sys.path.append('.')

from puppyparachute.store import load_db, freeze_db
from puppyparachute.tools import tracing, check, checking, short_diff_db


# Define two versions of f with the same name
def f(x):
    return x.upper()
f1 = f

def f(x):
    return x.lower()
f2 = f

def g(x):
    return x.split()[0]
f3 = g


f1_behavior = '''!RunStore
test_tools:f: !Function
  Cardinality: Single parameter list
  Known calls:
  - !Call
    Arguments:
      x: Traced code
    Cardinality: Single possible effect
    Effects list:
    - !Effect
      Returns: TRACED CODE
'''


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('test_check.yml', 'w') as fd:
            fd.write(f1_behavior)

    '''@classmethod
    def tearDownClass(cls):
        rm('test_check.yml')
        rm('test_check-last.yml')
    '''

    def setUp(self):
        sys.settrace(None)

    def test_with_tracing(self):
        with tracing(trace_all=True) as store:
            f('Traced code')
        self.assertEqual(
            list(store.keys()),
            [__name__ + ':f'],  # Qualified name of the function
        )

    def test_check_when_correct(self):
        # Write expected behavior like it's always been there
        # Clean up residues
        last_path = 'test_check-last.yml'
        rm(last_path)
        # Run a trace
        with tracing(trace_all=True) as store:
            f1('Traced code')
        # It's correct, so keep quiet
        check('test_check', store)
        # Do NOT dump the store
        self.assertFalse(os.path.exists(last_path))

    def test_check_after_code_change(self):
        # Write expected behavior like it's always been there
        with open('test_check.yml', 'w') as fd:
            fd.write(f1_behavior)
        # Clean up residues
        last_path = 'test_check-last.yml'
        rm(last_path)
        # Run a trace
        with tracing(trace_all=True) as store:
            f2('Traced code')
        # Something has changed, tell us about it
        with self.assertRaises(AssertionError) as cm:
            check('test_check', store)
        # Write the new behavior and tell us where
        self.assertIn(last_path, str(cm.exception))
        self.assertTrue(os.path.exists(last_path))

    def test_checking(self):

        def fake_trace(*args):
            return
        old_trace = sys.gettrace()
        sys.settrace(fake_trace)

        with self.assertRaises(AssertionError):
            # We know f1's behavior but we run f2, raise attention on it
            with checking(name='test_check', trace_all=True):
                f2('Traced code')

        # It has created a summary file
        self.assertTrue(os.path.exists('test_check-last-change.txt'))
        with open('test_check-last-change.txt') as f:
            change = f.read()
        change_lines = change.splitlines()
        self.assertEqual(len(change_lines), 1)
        self.assertIn('test_tools:f', change)
        self.assertEqual(change[0], '!')

        # It has put our trace function back
        after_trace = sys.gettrace()
        sys.settrace(old_trace)
        self.assertEqual(after_trace, fake_trace)

    def test_load_store(self):
        store = load_db(open('test_check.yml'))
        #import IPython; IPython.embed()
        self.assertIn('test_tools:f', store)

    def test_short_diff(self):
        with tracing(trace_all=True) as fndb1:
            f1('Traced code')
        with tracing(trace_all=True) as fndb2:
            f2('Traced code')
        with tracing(trace_all=True) as fndb3:
            f3('Traced code')
        store1 = freeze_db(fndb1)
        store2 = freeze_db(fndb2)
        store3 = freeze_db(fndb3)
        self.assertEqual(
            short_diff_db(store1, store1), '')
        self.assertEqual(
            short_diff_db(store1, store2),
            '! test_tools:f: x=Traced code -> traced code',
        )
        self.assertEqual(
            short_diff_db(store1, store3),
            '- test_tools:f: x=Traced code -> TRACED CODE\n'
            '+ test_tools:g: x=Traced code -> Traced'
        )


def rm(path):
    try:
        os.remove(path)
    except:
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
