

#? what=that -> Done something different
def do_things(what):
    print('Doing {}'.format(what))
    if 'a' in what:
        return 'Done something different'
    return 'Done'


class A(object):
    #? self=A {}, n=10 -> None | self=A {n: 10}
    def __init__(self, n):
        self.n = n

    #? i=2, self=A {n: 10} -> None | self=A {n: 12}
    def inc(self, i):
        self.n += i


#?  -> Everything is alright
def main():
    do_things('this')
    do_things('that')

    a = A(10)
    a.inc(2)

    return 'Everything is alright'
