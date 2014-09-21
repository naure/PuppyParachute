
from collections import defaultdict, namedtuple
import yaml

from .utils import values_sorted_by_key, dictmap

TAG = '!!tag:nau.re/puppyparachute,2014:'
STORE_TAG = '!TestRun'

# Runtime data structures. 'calls' and 'effects' will be
# dict of sorting keys. Later they will be replaced by lists.
FunctionsDB = type('FunctionsDB', (defaultdict, ), {})
Function = namedtuple('Function', ['calls'])
Call = namedtuple('Call', ['args', 'effects'])
Effect = namedtuple('Effect', [
    'returns', 'local_changes', 'calls_made', 'exception'])

# Create the runtime structures. Link them using defaultdict
def newFunctionsDB():
    return FunctionsDB(newFunction)

def newFunction():
    return Function(defaultdict(newCall))

def newCall():
    return Call({}, defaultdict(dict))

# Dumping the whole store
def FunctionsDB_freeze(obj):
    ' Translate the runtime db into a final store that can be dumped '
    return dictmap(Func_freeze, obj)

def FunctionsDB_repr(dumper, obj):
    return dumper.represent_mapping(STORE_TAG, FunctionsDB_freeze(obj))

# Dumping a function
def Func_freeze(obj):
    length = len(obj.calls)
    if length == 1:
        msg = 'Single parameter list'
    else:
        msg = '{} known parameter lists'.format(length)
    calls = values_sorted_by_key(obj.calls)
    return {
        'cardinality': msg,
        'parameters lists': list(map(Call_freeze, calls))
    }
'''
def Func_repr(dumper, obj):
    return dumper.represent_mapping(
        '!Function',
        Func_freeze(obj),
    )
'''

# Dumping a call
def Call_freeze(obj):
    length = len(obj.effects)
    if length == 1:
        msg = 'Single possible effect'
    else:
        msg = '{} different effects, depends on side-effects!'.format(length)
    return {
        'cardinality': msg,
        'effects list': values_sorted_by_key(obj.effects),
        'args': obj.args,
    }
'''
def Call_repr(dumper, obj):
    return dumper.represent_mapping(
        '!Call',
        Call_freeze(obj),
    )
'''

# Dumping a call effect
def Effect_repr(dumper, obj):
    ' Custom dump, avoid empty items, use flow style for calls_made '
    values = []
    if obj.calls_made is not None:
        values.append((
            dumper.represent_str('calls_made'),
            dumper.represent_sequence(
                'tag:yaml.org,2002:seq', obj.calls_made, True),
        ))
    if obj.exception:
        values.append((
            dumper.represent_str('exception'),
            dumper.represent_str(obj.exception[0]),
        ))
    if obj.local_changes is not None:
        values.append((
            dumper.represent_str('local_changes'),
            dumper.represent_dict(obj.local_changes),
        ))
    if obj.returns is not None:
        values.append((
            dumper.represent_str('returns'),
            dumper.represent_str(obj.returns),
        ))
    return yaml.MappingNode('tag:yaml.org,2002:map', values)

yaml.add_representer(FunctionsDB, FunctionsDB_repr)
#yaml.add_representer(Function, Func_repr)
#yaml.add_representer(Call, Call_repr)
yaml.add_representer(Effect, Effect_repr)

freeze_db = FunctionsDB_freeze

def format_db(db):
    return yaml.dump(db, default_flow_style=False)

# Load back from file or string
def Store_constructor(loader, node):
    return loader.construct_mapping(node)

yaml.add_constructor(STORE_TAG, Store_constructor)

def load_db(s):
    return yaml.load(s)
