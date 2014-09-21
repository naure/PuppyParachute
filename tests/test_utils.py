#!/usr/bin/env python3
import unittest
from pprint import pprint
from puppyparachute.utils import stable_hash


def order(seq):
    return sorted((stable_hash(p), p) for p in seq)


class Test(unittest.TestCase):
    def test_stable_hash(self):
        # XXX Not testing automatically
        phrases = [
            'Hé! 12',
            'Hé! 21',
            'Rien à voir',
            'Coucou par ici! Ca va?',
            'Coucou par la! Ca va?',
            'Coucou par la! Ca va bien?',
            'Coucou toi! Ca va bien?',
            'Coucou chez toi! Ca va bien?',
            'Phrase totalement différente',
        ]
        prefixed = ['prefix ' + p for p in phrases]
        suffixed = [p + ' suffix' for p in phrases]
        presufed = ['prefix ' + p + ' suffix' for p in phrases]

        hd_phrases = order(phrases)
        hd_prefixed = order(prefixed)
        hd_suffixed = order(suffixed)
        hd_presufed = order(presufed)

        pprint(hd_phrases)
        print()
        pprint(hd_prefixed)
        print()
        pprint(hd_suffixed)
        print()
        pprint(hd_presufed)


if __name__ == '__main__':
    unittest.main()
