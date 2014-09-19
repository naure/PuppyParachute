
from collections import defaultdict, namedtuple
from difflib import ndiff
import yaml

from .utils import (
    values_sorted_by_key,
    color_diffline,
)

FunctionsDB = type('FunctionsDB', (defaultdict, ), {})
Function = namedtuple('Function', ['calls'])
Call = namedtuple('Call', ['args', 'effects'])
Effect = namedtuple('Effect', ['returns', 'local_changes', 'calls_made'])

def newFunctionsDB():
    return FunctionsDB(newFunction)

def newFunction():
    return Function(defaultdict(newCall))

def newCall():
    return Call({}, defaultdict(dict))

def FunctionsDB_repr(dumper, obj):
    return dumper.represent_mapping('!FunctionsDB', obj)

def Func_repr(dumper, obj):
    length = len(obj.calls)
    if length == 1:
        msg = 'Single parameter list'
    else:
        msg = '{} known parameter lists'.format(length)
    return dumper.represent_mapping(
        '!Function',
        {'cardinality': msg,
         'parameters lists': values_sorted_by_key(obj.calls),
         })

def Call_repr(dumper, obj):
    length = len(obj.effects)
    if length == 1:
        msg = 'Single possible effect'
    else:
        msg = '{} different effects, depends on side-effects!'.format(length)
    return dumper.represent_mapping(
        '!Call',
        {'cardinality': msg,
         'effects list': values_sorted_by_key(obj.effects),
         'args': obj.args,
         })

def Effect_repr(dumper, obj):
    return dumper.represent_mapping(
        '!Effect', obj.__dict__)

yaml.add_representer(FunctionsDB, FunctionsDB_repr)
yaml.add_representer(Function, Func_repr)
yaml.add_representer(Call, Call_repr)
yaml.add_representer(Effect, Effect_repr)


def format_db(db):
    return yaml.dump(db)


def diff_db(db1, db2):
    s1 = format_db(db1)
    s2 = format_db(db2)
    difflines = ndiff(s1.splitlines(), s2.splitlines())
    colorlines = map(color_diffline, difflines)
    return '\n'.join(colorlines)
