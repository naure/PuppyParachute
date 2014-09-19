#!/usr/bin/env python3
import os
import yaml
from difflib import ndiff

from .trace import (
    start_trace, stop_trace,
)
from .store import (
    newFunctionsDB, format_db,
)
from .diff_utils import (
    udiff, red, color_diffline, diff_dict,
)


def find_changes(dba, dbb):
    return diff_dict(
        dba,
        dbb,
        lambda a, b: a == b and 'Same' or 'Changed'
    )

def smart_diff_db(dba, dbb):
    return yaml.dump(
        find_changes(dba, dbb),
        default_flow_style=False,
    )


def diff_db(db1, db2):
    s1 = format_db(db1)
    s2 = format_db(db2)
    difflines = ndiff(s1.splitlines(), s2.splitlines())
    colorlines = map(color_diffline, difflines)
    return '\n'.join(colorlines)


class TracingContext(object):
    def __init__(self, existing_store=None, **kwargs):
        if existing_store is None:
            self.fndb = newFunctionsDB()
        else:
            self.fndb = existing_store
        self.kwargs = kwargs

    def __enter__(self):
        self.orig_trace = start_trace(self.fndb, **self.kwargs)
        return self.fndb

    def __exit__(self, exc_type, exc_value, traceback):
        stop_trace(self.orig_trace)
        return False


def check(store_name, store):
    ' Load `store_name` and compare it to `store` '
    test_s = format_db(store)
    test_path = '{}-last.yml'.format(store_name)

    ref_path = '{}.yml'.format(store_name)
    if not os.path.exists(ref_path):
        open(ref_path, 'w').close()

    with open(ref_path) as f:
        ref_s = f.read()

    diff = udiff(ref_s, test_s, fromfile=ref_path, tofile=test_path)
    if diff:
        print(diff)
        with open(test_path, 'w') as f:
            f.write(test_s)
        raise AssertionError(red(
            'Behavior {} has changed. '
            'Check the diff. If it looks like what you are trying to do, '
            'copy {} over {} and commit it along with the code.'
            .format(store_name, test_path, ref_path)
        ))


class CheckingContext(TracingContext):
    ' A context manager that combines tracing() and check() '
    def __init__(self, name, **kwargs):
        tracing.__init__(self, **kwargs)
        self.name = name

    def __exit__(self, *args):
        tracing.__exit__(self, *args)
        check(self.name, self.fndb)
        return False

# Aliases for "with tracing() as db"
tracing = TracingContext
checking = CheckingContext
