#!/usr/bin/env python3
import sys
from collections import namedtuple
import yaml

from .utils import (
    stable_hash,
    strong_hash,
)
from .diff_utils import diff_dict

from .store import (
    newFunctionsDB,
    Effect,
)


# XXX qualname not always available
def fnid(frame):
    soi = frame.f_locals.get('self')
    classname = '' if soi is None else soi.__class__.__qualname__ + '.'
    module = frame.f_globals['__name__']
    return '{}:{}{}'.format(
        module,
        classname,
        frame.f_code.co_name,
    )

def split_fnid(s):
    ' Return [module name, function name] '
    return s.split(':', 1)

# Order-stable hashes (integers)
def hash_args(args):
    return stable_hash(serialize(args))

def hash_call_effect(effect):
    return stable_hash(serialize(effect))

# Alternative random-order hashes
def hash_args_rand(args):
    return 'args-{}'.format(hash_obj(args).decode())

def hash_call_effect_rand(effect):
    return 'effects-{}'.format(hash_obj(effect).decode())

def hash_obj(s):
    return strong_hash(serialize(s))

def serialize(o):
    try:
        s = yaml.dump(o, default_flow_style=True)
        if s.endswith('\n...\n'):
            return s[:-5]
        else:
            return s.strip()
    except TypeError:
        return '<object>'


Frame = namedtuple('Frame', ['gvars', 'gsnap', 'lvars', 'lsnap', 'calls_made'])


def snapshot_frame(frame):
    gnames = frame.f_code.co_names
    gvars = frame.f_globals
    lvars = frame.f_locals
    return Frame(gvars, snapshot_dict(gvars, gnames),
                 lvars, snapshot_dict(lvars),
                 [])


def snapshot_dict(d, keys=None):
    if keys is None:
        keys = d.keys()
    return {key: serialize(d.get(key)) for key in keys}


def find_local_changes(call_frame):
    old_snap = call_frame.lsnap
    # Take a snapshot of the same objects to see if they have changed
    new_snap = snapshot_dict(call_frame.lvars, old_snap.keys())
    # XXX Can use a better diff function
    return diff_dict(old_snap, new_snap)


def make_tracer(fndb, trace_all=False, packages=[]):

    if not packages:
        # Trace into any package
        def should_trace(funcid):
            return True
    else:
        # Trace only into selected packages, .modules, :classes
        def should_trace(funcid):
            return any(funcid.startswith(p) for p in packages)

    call_stack = []
    last_return_effect = [None]

    def trace_body(frame, event, ret_value):

        if event == 'exception':
            # XXX Ugly scope and immutability hacks; find a better way
            effect = last_return_effect[0]
            if effect:
                effect.exception = serialize(ret_value[1])
                last_return_effect[0] = None

        elif event == 'return':

            call_frame = call_stack.pop()
            local_changes = find_local_changes(call_frame)
            returns = None if ret_value is None else serialize(ret_value)

            func = fndb[fnid(frame)]
            args = call_frame.lsnap
            args_id = hash_args(args)
            call = func.calls[args_id]

            effect = Effect(
                calls_made=call_frame.calls_made or None,
                exception=None,
                local_changes=local_changes or None,
                returns=returns,
            )
            effect_id = hash_call_effect(effect)

            call.args.update(args)  # XXX Only the firts time, do differently
            call.effects[effect_id] = effect
            # Keep track of it in case it has raised an exception
            last_return_effect[0] = effect

        return trace_body

    def trace_calls(frame, event, value):

        filename = frame.f_code.co_filename
        funcname = frame.f_code.co_name
        funcid = fnid(frame)

        if not trace_all and (
            not should_trace(funcid) or
            filename.startswith('/') or
            filename.startswith('<') or
            funcname.startswith('<')
        ):
            return  # Ignore built-in, library calls, generators, ..
            # XXX Not very reliable

        if event == 'call':
            snapped_frame = snapshot_frame(frame)

            if call_stack:
                parent_frame = call_stack[-1]
                parent_frame.calls_made.append(funcname)

            call_stack.append(snapped_frame)
            return trace_body

    return trace_calls


def start_trace(fndb, **kwargs):
    tracer = make_tracer(fndb, **kwargs)
    orig_trace = sys.gettrace()
    sys.settrace(tracer)
    return orig_trace


stop_trace = sys.settrace


def trace(fn, fn_args=[], fn_kwargs={}, fndb=None, **kwargs):
    if fndb is None:
        fndb = newFunctionsDB()

    orig_trace = start_trace(fndb, **kwargs)
    #try:
    ret = fn(*fn_args, **fn_kwargs)  # Run it!
    #except Exception as exc:
    #    # XXX Determine if error is in user 'fn' or in trace code
    #    ret = exc
    stop_trace(orig_trace)
    return fndb, ret
