import os
import re

from .trace import split_fnid


def module_from_file(filename):
    assert filename[-3:] == '.py', 'Not a .py filename'
    return filename[:-3].replace(os.sep, '.')

re_def = re.compile(r'([ ]*) (class|def) [ ]+ (\w+)', re.X)

re_yaml_tag = re.compile(r'!!python/[^:]*:')

def remove_tags(s):
    return re_yaml_tag.sub('', s)

def format_args(args):
    return ', '.join('%s=%s' % item for item in args.items())

def format_fn(fn):
    call = fn['parameters lists'][0]  # First call example
    effect = call['effects list'][0]  # First known effect
    return remove_tags('{} -> {}{}'.format(
        format_args(call['args']),
        effect.returns,
        ' | ' + format_args(effect.local_changes)
        if effect.local_changes else '',
    ))

def annotate(store, filename):
    dottedfile = module_from_file(filename)
    fns = {}
    for qualname, fn in store.items():
        modname, fname = split_fnid(qualname)
        if dottedfile.endswith(modname):
            fns[fname] = fn

    outfile = '{}-traced.py'.format(filename)
    with open(filename) as in_fd, open(outfile, 'w') as out_fd:
        stack = []

        for line in in_fd:
            m = re_def.match(line)
            if m:
                indent, kw, defname = m.groups()
                level = len(indent) // 4
                stack = stack[:level]
                if kw == 'class':
                    stack.append(defname)
                if stack and len(stack) == level:  # Directly under a class
                    qname = '{}.{}'.format('.'.join(stack), defname)
                else:
                    qname = defname
                fn = fns.get(qname)
                if fn:
                    out_fd.write('{}#? {}\n'.format(
                        indent,
                        format_fn(fn),
                    ))
            out_fd.write(line)
