from unittest.mock import MagicMock
import unittest

from renderscript.interpreter import Interpreter
from renderscript import structure


class InterpreterTests(unittest.TestCase):

    def test_interpreter(self):
        test_cases = [
            (
                structure.Bool(True),
                True,
            ),
            (
                structure.Bool(False),
                False,
            ),
            (
                structure.Number(10),
                10,
            ),
            (
                structure.Number(24.0),
                24.0,
            ),
            (
                structure.String("hello"),
                "hello",
            ),
            (
                structure.List([
                    structure.Number(10),
                    structure.String("hello"),
                    structure.Bool(False)
                ]),
                [10, "hello", False],
            ),
            (
                structure.MakeMap([
                    (structure.String("hello"), structure.Number(24)),
                    (structure.Number(15), structure.Bool(False)),
                    (structure.Bool(True), structure.String("hi")),
                ]),
                {
                    "hello": 24,
                    15: False,
                    True: "hi",
                },
            ),
            (
                structure.Do([
                    structure.Let(structure.Identifier("x"), structure.Number(10)),
                    structure.Identifier("x"),
                ]),
                10,
            ),
            (
                structure.ForEach(
                    structure.Identifier("x"),
                    structure.List([
                        structure.String("hello"),
                        structure.Number(10)
                    ]),
                    structure.Identifier("x"),
                ),
                ["hello", 10],
            ),
            (
                structure.If(
                    structure.Bool(True),
                    structure.String("Hello"),
                    structure.String("Hi"),
                ),
                "Hello",
            ),
            (
                structure.If(
                    structure.Bool(False),
                    structure.String("Hello"),
                    structure.String("Hi"),
                ),
                "Hi",
            ),
            (
                structure.If(
                    structure.Bool(True),
                    structure.Do([
                        structure.String("Hello"),
                    ]),
                    structure.String("Hi"),
                ),
                "Hello",
            ),
            (
                structure.Comment("hello"),
                None,
            ),
        ]

        for input_structure, expected_output in test_cases:
            with self.subTest(str(input_structure)):
                visitor = Interpreter()
                result = visitor.accept(input_structure)
                self.assertEqual(expected_output, result, "interpreted result should match expected output")

    @staticmethod
    def test_call_behaviour():
        mock_log_function = MagicMock()
        visitor = Interpreter()
        visitor.register_external_call('log', mock_log_function)
        visitor.accept(
            structure.Call(
                structure.Identifier('log'),
                [
                    structure.Number(10),
                    structure.String("hello"),
                    structure.Bool(False),
                ]
            )
        )
        mock_log_function.assert_called_with(
            visitor.accept,
            'log',
            structure.Number(10),
            structure.String("hello"),
            structure.Bool(False)
        )
