from . import structure as s
import re


def equals(evaluate, _name, *args):
    evaluated = [evaluate(arg) for arg in args]
    for index, arg in enumerate(evaluated[1:], start=1):
        if arg != evaluated[index - 1]:
            return False
    return True


def split(evaluate, _name, regex, text, *args):
    flags = 0
    known_flags = dict([
        (name, getattr(re, name.upper()))
        for name in [
            "multiline",
        ]
    ])
    for arg in args:
        if isinstance(arg, s.Identifier):
            if arg.label not in known_flags:
                raise Exception(f"{arg.label} is not a known regex flag")
            flags |= known_flags[arg.label]
        else:
            raise Exception("split only accepts additional arguments as regex flag identifiers")
    return re.split(evaluate(regex), evaluate(text), flags=flags)


def splitlines(evaluate, _name, text):
    return evaluate(text).splitlines()


def append(evaluate, _name, *args):
    evaluated = [evaluate(arg) for arg in args]
    result = evaluated[0]
    for arg in evaluated[1:]:
        result += arg
    return result


def length(evaluate, _name, collection):
    return len(evaluate(collection))


def register_builtins(interpreter):
    builtins = [
        equals,
        split,
        splitlines,
        append,
        length
    ]
    for builtin in builtins:
        interpreter.register_external_call(builtin.__name__, builtin)
