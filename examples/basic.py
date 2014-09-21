
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

def main():
    f('Traced code')
