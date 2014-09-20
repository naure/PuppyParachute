from base64 import b64encode
from zlib import crc32
from hashlib import sha1


def stable_hash(s):
    return sum(map(ord, s)) << 32 | (
        crc32(s.encode()) & 0xffffffff)
    # XXX Ensure < 64bits. Use stronger algo.

def strong_hash(s, l=6):
    return b64encode(sha1(s.encode()).digest()[:l])

def values_sorted_by_key(d):
    return [val for key, val in sorted(d.items())]

def truncate(s, size=80):
    " Truncate the middle of a string if it's too long "
    ls = len(s)
    if ls <= size:
        return s
    else:
        lend = size // 3
        lstart = size - 3 - lend
        return '{}...{}'.format(
            s[:lstart],
            s[-lend:],
        )
