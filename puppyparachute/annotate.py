import os
import re
from itertools import filterfalse

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
    call = fn.known_calls[0]  # First call example
    effect = call.effects_list[0]  # First known effect
    return remove_tags('{} -> {}{}'.format(
        format_args(call.arguments),
        effect.returns,
        ' | ' + format_args(effect.local_changes)
        if effect.local_changes else '',
    ))

# Annotating
def annotate_s(store, lines, filename):
    dottedfile = module_from_file(filename)
    fns = {}
    for qualname, fn in store.items():
        modname, fname = split_fnid(qualname)
        if dottedfile.endswith(modname) or modname == '__main__':
            fns[fname] = fn

    stack = []
    for line in filter_annotations(lines):
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
                yield '{}#? {}'.format(
                    indent,
                    format_fn(fn),
                )
        yield line


def annotate(store, infile, outfile=None):
    ' Annotate `infile` using functions records in `store` '
    if not outfile:
        outfile = infile
    with open(infile) as in_fd:
        inlines = in_fd.read().splitlines()
    outlines = annotate_s(store, inlines, infile)
    with open(outfile, 'w') as out_fd:
        out_fd.write('\n'.join(outlines))
        out_fd.write('\n')

# Deannotating
re_annotation = re.compile(r'\s*#\?')

def filter_annotations(lines):
    ' Remove annotations from list of `lines` '
    return filterfalse(re_annotation.match, lines)

def deannotate(infile, outfile=None):
    ' Remove annotations from `infile` '
    if not outfile:
        outfile = infile
    with open(infile) as in_fd:
        inlines = in_fd.read().splitlines()
    outlines = filter_annotations(inlines)
    with open(outfile, 'w') as out_fd:
        out_fd.write('\n'.join(outlines))
        out_fd.write('\n')
