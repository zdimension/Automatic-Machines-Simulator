# coding: utf-8

from am.commands import cmd


def get_dupl(am):
    cache = {}
    dupl = {}
    for state, transitions in am.transitions.items():
        fs = frozenset(transitions.items())
        if fs in cache:
            if fs not in dupl:
                dupl[fs] = [cache[fs]]
            dupl[fs].append(state)
        else:
            cache[fs] = state
    return dupl


def get_unreachable(am):
    reached = {ns for state, transitions in am.transitions.items() for w, m, ns in transitions.values() if ns != state}
    return set(am.transitions) - {am.initial_state} - reached


def get_redundant(am):
    return {state: next(iter(transitions.values()))[2] for state, transitions in am.transitions.items() if
            len({ns for w, m, ns in transitions.values()}) == 1 and
            not any(1 for r, (w, m, ns) in transitions.items() if r != w or any(m))}


def replace_state(am, old, new):
    repl = lambda x: new if x == old else x
    am.initial_state = repl(am.initial_state)
    am.end_states = {repl(k): v for k, v in am.end_states.items()}
    am.undefined_state = repl(am.undefined_state[0]), am.undefined_state[1]
    am.transitions = {state: {read: (write, move, repl(next)) for read, (write, move, next) in trans.items()}
                      for state, trans in am.transitions.items()}
    del am.transitions[old]


def remove_redundant(am):
    while True:
        redun = get_redundant(am)
        if not redun:
            break
        for state, next in redun.items():
            replace_state(am, state, next)
            break


@cmd()
def analysis(am, **kwargs):
    """
    Checks for potential optimizations and unreachable code in an automatic machine.
    """
    print("Analysis of machine:", am.name)
    print("Unreachable states:", ", ".join(sorted(get_unreachable(am))) or "None")
    dupl = get_dupl(am)
    print("Duplicate states (can be merged):",
          ", ".join("(" + ", ".join(sorted(x)) + ")" for x in dupl.values()) or "None")
    print("Redundant states:", ", ".join(sorted(get_redundant(am))) or "None")


@cmd([
    ("-a", "--aggressive", "remove states that do not move the tape", False, "store_true"),
])
def optimize(am, aggressive=False, **kwargs):
    """
    Optimizes an automatic machine.
    """
    for state in get_unreachable(am):
        del am.transitions[state]
    if aggressive:
        remove_redundant(am)
    print(am.get_code())
