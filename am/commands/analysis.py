# coding: utf-8
from am.commands import cmd


@cmd()
def analysis(am, **kwargs):
    print("Analysis of machine:", am.name)
    reached = {ns for state, transitions in am.transitions.items() for w, m, ns in transitions.values() if ns != state}
    print("Unreachable states:", ", ".join(set(am.transitions) - {am.initial_state} - reached))
