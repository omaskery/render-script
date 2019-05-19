import unittest


from renderscript.interpreter import Interpreter
from renderscript import structure as s
import renderscript.builtin_functions as builtins


class TestBuiltinFunctions(unittest.TestCase):

    def test_functions(self):
        test_cases = [
            (builtins.equals, (), True),
            (builtins.equals, (s.Bool(True),), True),
            (builtins.equals, (s.Bool(True), s.Bool(True)), True),
            (builtins.equals, (s.Bool(True), s.Bool(False)), False),
            (builtins.equals, (s.Bool(False), s.Bool(True)), False),
            (builtins.equals, (s.Bool(True), s.Bool(True), s.Bool(True)), True),
            (builtins.equals, (s.Number(10), s.Bool(True)), False),
            (builtins.split, (s.String("\n"), s.String("hello\nthere")), ["hello", "there"]),
            (builtins.append, (s.String("hello "), s.String("world!")), "hello world!"),
        ]

        for fn, args, expected_result in test_cases:
            with self.subTest(f"{fn.__name__}({', '.join(map(str, args))})"):
                interpreter = Interpreter()
                result = fn(interpreter.accept, fn.__name__, *args)
                self.assertEqual(expected_result, result, "function result should match expected result")
