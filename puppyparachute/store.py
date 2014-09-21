
from collections import defaultdict, namedtuple
import yaml

from .utils import (
    values_sorted_by_key, dictmap,
    nice_name, nice_dict, ugly_dict,
)

TAG = '!!tag:nau.re/puppyparachute,2014:'
STORE_TAG = '!RunStore'

# Runtime data structures. 'calls' and 'effects' will be
# dict of sorting keys. Later they will be replaced by lists.
FunctionsDB = type('FunctionsDB', (defaultdict, ), {})
Function = namedtuple('Function', ['calls'])
Call = namedtuple('Call', ['args', 'effects'])
Effect_fields = [
    'returns', 'local_changes', 'calls_made', 'exception']

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
    return RunStore(**dictmap(Func_freeze, obj))

# Dumping a function
def Func_freeze(obj):
    length = len(obj.calls)
    if length == 1:
        msg = 'Single parameter list'
    else:
        msg = '{} known parameter lists'.format(length)
    calls = values_sorted_by_key(obj.calls)
    return StFunction(
        cardinality=msg,
        known_calls=list(map(Call_freeze, calls)),
    )

# Dumping a call
def Call_freeze(obj):
    length = len(obj.effects)
    if length == 1:
        msg = 'Single possible effect'
    else:
        msg = '{} different effects, depends on side-effects!'.format(length)
    effects = values_sorted_by_key(obj.effects)
    return StCall(
        cardinality=msg,
        effects_list=list(map(Effect_freeze, effects)),
        arguments=obj.args,
    )

def Effect_freeze(obj):
    return StEffect(**obj.__dict__)

# Storage and usage data structures
class O(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        self.__dict__ = self

class RunStore(O):
    yaml_tag = '!RunStore'
class StFunction(O):
    yaml_tag = '!Function'
class StCall(O):
    yaml_tag = '!Call'
class StEffect(O):
    yaml_tag = '!Effect'

    def __init__(self, **kwargs):
        O.__init__(self, **kwargs)
        for f in Effect_fields:
            self.setdefault(f, None)

Effect = StEffect

# Dump and load back from file or string
def register_class(cls, nice=True):
    def St_represent(dumper, obj):
        mapping = nice_dict(obj) if nice else obj
        return dumper.represent_mapping(cls.yaml_tag, mapping)

    def St_construct(loader, node):
        mapping = loader.construct_mapping(node)
        attrs = ugly_dict(mapping) if nice else mapping
        return cls(**attrs)

    yaml.add_representer(cls, St_represent)
    yaml.add_constructor(cls.yaml_tag, St_construct)

register_class(RunStore, nice=False)
register_class(StFunction)
register_class(StCall)
register_class(StEffect)


# Dumping a call effect is special to optimize the rendering
def Effect_repr(dumper, obj):
    ' Custom dump, avoid empty items, use flow style for calls_made '
    values = []
    if obj.calls_made is not None:
        # Render calls_made as a flow list
        values.append((
            dumper.represent_str(nice_name('calls_made')),
            dumper.represent_sequence(
                'tag:yaml.org,2002:seq', obj.calls_made, True),
        ))
    if obj.exception is not None:
        values.append((
            dumper.represent_str(nice_name('exception')),
            dumper.represent_str(obj.exception),
        ))
    if obj.local_changes is not None:
        values.append((
            dumper.represent_str(nice_name('local_changes')),
            dumper.represent_dict(obj.local_changes),
        ))
    if obj.returns is not None:
        values.append((
            dumper.represent_str(nice_name('returns')),
            dumper.represent_str(obj.returns),
        ))
    return yaml.MappingNode(StEffect.yaml_tag, values)

yaml.add_representer(StEffect, Effect_repr)

def FunctionsDB_repr(dumper, obj):
    ' Convert to RunStore and dump that '
    return dumper.represent_data(FunctionsDB_freeze(obj))

yaml.add_representer(FunctionsDB, FunctionsDB_repr)


# Convenience functions
freeze_db = FunctionsDB_freeze

def format_db(db):
    return yaml.dump(db, default_flow_style=False)

def load_db(s):
    return yaml.load(s)
