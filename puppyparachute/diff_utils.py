import difflib
import pprint
from .colors import red, green


def diff_plus(s1, s2):
    " Diff strings s1 and s2 and print new/different lines of s2 "
    difflines = difflib.ndiff(
        s1.splitlines(),
        s2.splitlines(),
    )
    pluslines = (l[2:] for l in difflines if l.startswith('+ '))
    return '\n'.join(pluslines)

def diff_dict(d1, d2, diff_fn=diff_plus):
    " Diff values in d1 and d2 per key "
    diffs = {}
    keys = set(d1).union(d2)
    for key in keys:
        diff = diff_fn(d1.get(key, ''), d2.get(key, ''))
        if diff:
            diffs[key] = diff
    return diffs

def compare_dict(da, db):
    " Find identical, changed, added, removed elements in dicts "
    sa = set(da)
    sb = set(db)
    common = sa.intersection(sb)
    changed = set(filter((lambda k: da[k] != db[k]), common))
    stayed = common - changed
    inserted = sb - sa
    removed = sa - sb
    return stayed, inserted, removed, changed

def diff_obj(d1, d2):
    if d1 == d2:
        return None
    else:
        diff = difflib.ndiff(
            pprint.pformat(d1).splitlines(),
            pprint.pformat(d2).splitlines())
        return '\n'.join(map(
            color_diffline,
            diff,
        ))

def color_diffline(line):
    if line.startswith('-'):
        return red(line)
    if line.startswith('+'):
        return green(line)
    return line

def color_number(n):
    return color_diffline('%+d' % n) if n else '0'

def udiff(a, b, **kwargs):
    return '\n'.join(map(
        color_diffline,
        difflib.unified_diff(
            a.splitlines(), b.splitlines(), **kwargs
        )))


def diff_paths(pa, pb):
    with open(pa) as fa, open(pb) as fb:
        a = fa.read()
        b = fb.read()

    if a != b:
        return udiff(a, b, fromfile=pa, tofile=pb)
    else:
        return False


def compare_paths(ref_path, test_path, what='Output'):
    test_diff = diff_paths(ref_path, test_path)
    if test_diff:
        print(red('{} {} is different than reference {}'.format(
            what, test_path, ref_path)))
        print(test_diff)
        return 1
    else:
        return 0
