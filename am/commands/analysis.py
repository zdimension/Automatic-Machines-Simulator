# coding: utf-8
from collections import defaultdict

from am.commands import cmd
from itertools import groupby

@cmd()
def analysis(am, **kwargs):
    """
    Checks for potential optimizations and unreachable code in an automatic machine.
    """
    print("Analysis of machine:", am.name)
    reached = {ns for state, transitions in am.transitions.items() for w, m, ns in transitions.values() if ns != state}
    print("Unreachable states:", ", ".join(set(am.transitions) - {am.initial_state} - reached))
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
    print("Duplicate states (can be merged):", ", ".join("(" + ", ".join(x) + ")" for x in dupl.values()))
