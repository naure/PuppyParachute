#!/usr/bin/env python3
import os
from difflib import ndiff

from .trace import (
    start_trace, stop_trace,
)
from .store import (
    newFunctionsDB, freeze_db, format_db, load_db
)
from .diff_utils import (
    udiff, diff_obj, color_diffline, compare_dict
)
from .utils import truncate
from .colors import green, red, orange
from .annotate import format_fn


def cmp_db(dba, dbb):
    stayed, inserted, removed, changed = compare_dict(dba, dbb)
    for k in removed:
        yield '{}: {}'.format(red('-' + k), truncate(format_fn(dba[k])))
    for k in inserted:
        yield '{}: {}'.format(green('+' + k), truncate(format_fn(dbb[k])))
    for k in changed:
        yield ' {}: {}'.format(orange(k), truncate(format_fn(dbb[k])))


def short_diff_db(a, b):
    return '\n'.join(cmp_db(a, b))


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
    test_store = freeze_db(store)
    test_path = '{}-last.yml'.format(store_name)
    last_change_path = '{}-last-change.txt'.format(store_name)

    ref_path = '{}.yml'.format(store_name)
    if not os.path.exists(ref_path):
        open(ref_path, 'w').close()
        ref_s = ''
        ref_store = {}
    else:
        with open(ref_path) as f:
            ref_s = f.read()
        ref_store = load_db(ref_s)

    with open(ref_path) as f:
        ref_s = f.read()

    diff = udiff(ref_s, test_s, fromfile=ref_path, tofile=test_path)
    if diff:
        print(diff)
        with open(test_path, 'w') as f:
            f.write(test_s)

        #change = short_diff_db(ref_store, test_store)
        change = diff_obj(ref_store, test_store)
        with open(last_change_path, 'w') as f:
            f.write(change)

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
