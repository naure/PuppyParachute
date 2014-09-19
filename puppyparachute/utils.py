
import difflib
import pprint
from base64 import b64encode
from zlib import crc32
from hashlib import sha1

from .colors import red, green


def stable_hash(s):
    return sum(map(ord, s)) << 32 | (
        crc32(s.encode()) & 0xffffffff)
    # XXX Ensure < 64bits. Use stronger algo.

def strong_hash(s, l=6):
    return b64encode(sha1(s.encode()).digest()[:l])

def values_sorted_by_key(d):
    return [val for key, val in sorted(d.items())]

def diff_dict(d1, d2):
    " Diff values in d1 and d2 per key "
    diffs = {}
    keys = set(d1).union(d2)
    for key in keys:
        diff = diff_plus(d1.get(key) or '', d2.get(key) or '')
        if diff:
            diffs[key] = diff
    return diffs

def diff_plus(s1, s2):
    " Diff strings s1 and s2 and print new/different lines of s2 "
    difflines = difflib.ndiff(
        s1.splitlines(),
        s2.splitlines(),
    )
    pluslines = (l[2:] for l in difflines if l.startswith('+ '))
    return '\n'.join(pluslines)

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
    if line.startswith('- '):
        return red(line)
    if line.startswith('+ '):
        return green(line)
    return line
