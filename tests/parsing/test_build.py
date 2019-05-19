import unittest
import typing


from renderscript import structure
from renderscript.parsing.source import StringSource, SourcePosition
from renderscript.parsing.tokeniser import Tokeniser, Token, TokenKinds
from renderscript.parsing.parser import parse, AstNode
from renderscript.parsing import build


class TestBuildInterpreter(unittest.TestCase):

    def test_build_atoms(self):
        test_cases = [
            (AstNode(_token(TokenKinds.IDENTIFIER, "hello"), []), structure.Identifier("hello")),
            (AstNode(_token(TokenKinds.NUMBER, "10"), []), structure.Number(10)),
            (AstNode(_token(TokenKinds.NUMBER, "24.8"), []), structure.Number(24.8)),
            (AstNode(_token(TokenKinds.BOOL, "true"), []), structure.Bool(True)),
            (AstNode(_token(TokenKinds.BOOL, "false"), []), structure.Bool(False)),
            (AstNode(_token(TokenKinds.STRING, "hello"), []), structure.String("hello")),
        ]
        for ast, expected_node in test_cases:
            with self.subTest(str(ast)):
                built_node = build.build_node(ast)
                self.assertEqual(expected_node, built_node)

    def test_build_compared_to_parsed(self):
        test_cases = [
            (
                '(exec-cmd "sh | include snmpv[12]")',
                structure.Call(structure.Identifier("exec-cmd"), [
                    structure.String('sh | include snmpv[12]'),
                ])
            ),
            (
                '(let test 10)',
                structure.Let(
                    structure.Identifier("test"),
                    structure.Number(10)
                )
            ),
            (
                '(let test (splitlines "what\na\nlovely\nday"))',
                structure.Let(
                    structure.Identifier("test"),
                    structure.Call(structure.Identifier('splitlines'), [
                        structure.String("what\na\nlovely\nday"),
                    ])
                )
            ),
            (
                '(if true 10 20)',
                structure.If(
                    structure.Bool(True),
                    structure.Number(10),
                    structure.Number(20),
                )
            ),
            (
                '(for-each cmd cmd_list (append "no " cmd))',
                structure.ForEach(
                    structure.Identifier("cmd"),
                    structure.Identifier("cmd_list"),
                    structure.Call(structure.Identifier("append"), [
                        structure.String("no "),
                        structure.Identifier("cmd"),
                    ]),
                )
            ),
            (
                '(list 1 2 3 "hello" test false)',
                structure.List([
                    structure.Number(1),
                    structure.Number(2),
                    structure.Number(3),
                    structure.String("hello"),
                    structure.Identifier("test"),
                    structure.Bool(False),
                ])
            ),
            (
                '(make-map "hello" 4 "bye" false 24 meow)',
                structure.MakeMap([
                    (structure.String("hello"), structure.Number(4)),
                    (structure.String("bye"), structure.Bool(False)),
                    (structure.Number(24), structure.Identifier("meow")),
                ])
            ),
        ]
        for source, expected_node in test_cases:
            with self.subTest(source):
                ast = self._parse_single(source)
                built_node = build.build_node(ast)
                self.assertEqual(expected_node, built_node)

    @classmethod
    def _parse_single(cls, text):
        ast = cls._parse(text)
        if len(ast) != 1:
            raise Exception("parse single must produce 1 top-level AST node")
        return ast[0]

    @staticmethod
    def _parse(text) -> typing.List[AstNode]:
        return parse(Tokeniser(StringSource(text)))


def _token(kind: TokenKinds, value: str, start_position: typing.Optional[SourcePosition] = None,
           end_position: typing.Optional[SourcePosition] = None) -> Token:
    return Token(
        kind,
        value,
        typing.cast(SourcePosition, start_position),
        typing.cast(SourcePosition, end_position)
    )
