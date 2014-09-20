
from collections import defaultdict, namedtuple
import yaml

from .utils import values_sorted_by_key

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
    ' Custom dump, avoid empty items, use flow style for calls_made '
    values = []
    if obj.local_changes is not None:
        values.append((
            dumper.represent_str('local_changes'),
            dumper.represent_dict(obj.local_changes),
        ))
    if obj.calls_made is not None:
        values.append((
            dumper.represent_str('calls_made'),
            dumper.represent_sequence(
                'tag:yaml.org,2002:seq', obj.calls_made, True),
        ))
    if obj.returns is not None:
        values.append((
            dumper.represent_str('returns'),
            dumper.represent_str(obj.returns),
        ))
    return yaml.MappingNode('!Effect', values)

yaml.add_representer(FunctionsDB, FunctionsDB_repr)
yaml.add_representer(Function, Func_repr)
yaml.add_representer(Call, Call_repr)
yaml.add_representer(Effect, Effect_repr)


def format_db(db):
    return yaml.dump(db, default_flow_style=False)
