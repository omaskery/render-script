import unittest

from renderscript.sexp_renderer import SexpVisitor
from renderscript import structure


class SexpRendererTests(unittest.TestCase):

    def test_rendering(self):
        test_cases = [
            (
                structure.Comment('hello'),
                ';hello',
            ),
            (
                structure.Bool(True),
                'true',
            ),
            (
                structure.Number(24),
                '24',
            ),
            (
                structure.String("hello"),
                '"hello"',
            ),
            (
                structure.List([]),
                '(list)',
            ),
            (
                structure.List([
                    structure.String("hello"),
                    structure.Number(10),
                    structure.Bool(False),
                ]),
                '(list "hello" 10 false)',
            ),
            (
                structure.List([
                    structure.String("hello"),
                    structure.Number(10),
                    structure.List([structure.String("wow")]),
                    structure.Bool(False),
                ]),
                '(list "hello" 10 (list "wow") false)',
            ),
            (
                structure.MakeMap({}),
                '(make-map)',
            ),
            (
                structure.MakeMap({
                    structure.String("hello"): structure.Number(10),
                }),
                '(make-map "hello" 10)',
            ),
            (
                structure.MakeMap({
                    structure.String("hello"): structure.MakeMap({
                        structure.Number(24): structure.List([
                            structure.Bool(True),
                            structure.Bool(False),
                        ]),
                    }),
                }),
                '(make-map "hello" (make-map 24 (list true false)))',
            ),
            (
                structure.If(
                    structure.Bool(True),
                    structure.Number(10),
                    structure.Number(24)
                ),
                '(if true 10 24)',
            ),
            (
                structure.Identifier("john"),
                'john'
            ),
            (
                structure.Let(
                    structure.Identifier("test"),
                    structure.Number(10)
                ),
                '(let test 10)',
            ),
            (
                structure.Let(
                    structure.Identifier("test"),
                    structure.List([
                        structure.Number(1),
                        structure.Number(2)
                    ])
                ),
                '(let test (list 1 2))',
            ),
            (
                structure.ForEach(
                    structure.Identifier('x'),
                    structure.List([
                        structure.Number(1),
                        structure.Number(2),
                        structure.Number(3)
                    ]),
                    structure.Identifier('x')
                ),
                '(for-each x (list 1 2 3) x)'
            ),
            (
                structure.Do([
                    structure.Identifier('x'),
                    structure.Identifier('y'),
                    structure.Number(10),
                ]),
                '(do x y 10)'
            ),
            (
                structure.Call(
                    structure.Identifier("log"),
                    [
                        structure.Identifier('x'),
                        structure.Identifier('y'),
                        structure.Number(10),
                    ]
                ),
                '(log x y 10)'
            ),
        ]

        for input_structure, expected_output in test_cases:
            with self.subTest(str(input_structure)):
                visitor = SexpVisitor()
                rendered = visitor.accept(input_structure)
                self.assertEqual(expected_output, rendered, "rendered output should match expected output")
