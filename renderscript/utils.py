import typing


from .parsing.source import StringSource
from .parsing.tokeniser import Tokeniser
from .parsing.parser import parse
from .parsing.build import build
from .structure import Node
from .interpreter import Interpreter
from .builtin_functions import register_builtins


def make_default_interpreter():
    interpreter = Interpreter()
    register_builtins(interpreter)
    return interpreter


def compile_script(script_source: str) -> typing.List[Node]:
    source = StringSource(script_source)
    tokeniser = Tokeniser(source)
    ast = parse(tokeniser)
    return build(ast)


def execute_compiled(compiled_script: typing.List[Node], interpreter: Interpreter) -> typing.Any:
    result = None
    for node in compiled_script:
        result = interpreter.accept(node)
    return result


def execute_script(script_source: str, interpreter: Interpreter = None) -> typing.Any:
    interpreter = interpreter or make_default_interpreter()

    compiled_script = compile_script(script_source)

    return execute_compiled(compiled_script, interpreter)
