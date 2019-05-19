import unittest
import typing

import renderscript.parsing.source
import renderscript.parsing.tokeniser
from renderscript.parsing.parser import AstNode
from renderscript.parsing.tokeniser import TokenKinds, Token
from renderscript.parsing.source import SourcePosition
from renderscript.parsing import parser


class TestParser(unittest.TestCase):

    def test_parse_atom(self):
        test_cases = [
            (
                [(TokenKinds.NUMBER, '10')],
                AstNode(_token(TokenKinds.NUMBER, '10'), [])
            ),
            (
                [(TokenKinds.STRING, 'hello')],
                AstNode(_token(TokenKinds.STRING, 'hello'), [])
            ),
            (
                [(TokenKinds.BOOL, 'true')],
                AstNode(_token(TokenKinds.BOOL, 'true'), [])
            ),
            (
                [(TokenKinds.IDENTIFIER, 'kittens')],
                AstNode(_token(TokenKinds.IDENTIFIER, 'kittens'), [])
            ),
        ]
        for tokens, expected_node in test_cases:
            with self.subTest(str(tokens)):
                tokeniser = self._tokeniser(*tokens)
                self.assertEqual(expected_node, parser.parse_atom(tokeniser))

    def test_parse_expression(self):
        test_cases = [
            (
                [
                    (TokenKinds.OPEN_PAREN, '('),
                    (TokenKinds.CLOSE_PAREN, ')'),
                ],
                AstNode(_token(TokenKinds.OPEN_PAREN, '('), []),
            ),
            (
                [
                    (TokenKinds.OPEN_PAREN, '('),
                    (TokenKinds.IDENTIFIER, 'exec-cmd'),
                    (TokenKinds.CLOSE_PAREN, ')'),
                ],
                AstNode(_token(TokenKinds.OPEN_PAREN, '('), [
                    AstNode(_token(TokenKinds.IDENTIFIER, 'exec-cmd'), []),
                ]),
            ),
            (
                [
                    (TokenKinds.OPEN_PAREN, '('),
                    (TokenKinds.IDENTIFIER, 'exec-cmd'),
                    (TokenKinds.STRING, 'sh | include snmpv[12]'),
                    (TokenKinds.CLOSE_PAREN, ')'),
                ],
                AstNode(_token(TokenKinds.OPEN_PAREN, '('), [
                    AstNode(_token(TokenKinds.IDENTIFIER, 'exec-cmd'), []),
                    AstNode(_token(TokenKinds.STRING, 'sh | include snmpv[12]'), []),
                ]),
            ),
            (
                [
                    (TokenKinds.OPEN_PAREN, '('),
                    (TokenKinds.IDENTIFIER, 'splitlines'),
                    (TokenKinds.OPEN_PAREN, '('),
                    (TokenKinds.IDENTIFIER, 'exec-cmd'),
                    (TokenKinds.STRING, 'sh | include snmpv[12]'),
                    (TokenKinds.CLOSE_PAREN, ')'),
                    (TokenKinds.CLOSE_PAREN, ')'),
                ],
                AstNode(_token(TokenKinds.OPEN_PAREN, '('), [
                    AstNode(_token(TokenKinds.IDENTIFIER, 'splitlines'), []),
                    AstNode(_token(TokenKinds.OPEN_PAREN, '('), [
                        AstNode(_token(TokenKinds.IDENTIFIER, 'exec-cmd'), []),
                        AstNode(_token(TokenKinds.STRING, 'sh | include snmpv[12]'), []),
                    ]),
                ]),
            ),
        ]
        for tokens, expected_node in test_cases:
            with self.subTest(str(tokens)):
                tokeniser = self._tokeniser(*tokens)
                self.assertEqual(expected_node, parser.parse_expression(tokeniser))

    def test_from_string_tokeniser(self):
        tokeniser = renderscript.parsing.tokeniser.Tokeniser(renderscript.parsing.source.StringSource("""
(let snmp_cmds
    (splitlines
        (exec-cmd "sh | include snmpv[12]")))

(if (equals (length snmp_cmds) 0)
    "no-issue"
    (do
        (let fixes
            (for-each cmd snmp_cmds
                (append "no " cmd)))
        (for-each cmd fixes
            (exec-cmd cmd))))
        """))

        parsed = parser.parse(tokeniser)

        def _blank_source_position_of_nodes(ast_node_list):
            return [
                _blank_source_position_of_node(node) for node in ast_node_list
            ]

        def _blank_source_position_of_node(ast_node):
            return AstNode(
                _token(ast_node.head.kind, ast_node.head.value),
                _blank_source_position_of_nodes(ast_node.tail)
            )

        parsed = _blank_source_position_of_nodes(parsed)

        def _sexp(*values: AstNode) -> AstNode:
            return AstNode(_token(TokenKinds.OPEN_PAREN, '('), list(values))

        def _ident(label) -> AstNode:
            return AstNode(_token(TokenKinds.IDENTIFIER, label), [])

        def _literal(kind, value) -> AstNode:
            return AstNode(_token(kind, value), [])

        expected_ast = [
            _sexp(
                _ident('let'),
                _ident('snmp_cmds'),
                _sexp(
                    _ident('splitlines'),
                    _sexp(
                        _ident('exec-cmd'),
                        _literal(TokenKinds.STRING, "sh | include snmpv[12]")
                    )
                )
            ),
            _sexp(
                _ident('if'),
                _sexp(
                    _ident('equals'),
                    _sexp(
                        _ident('length'),
                        _ident('snmp_cmds')
                    ),
                    _literal(TokenKinds.NUMBER, '0')
                ),
                _literal(TokenKinds.STRING, 'no-issue'),
                _sexp(
                    _ident('do'),
                    _sexp(
                        _ident('let'),
                        _ident('fixes'),
                        _sexp(
                            _ident('for-each'),
                            _ident('cmd'),
                            _ident('snmp_cmds'),
                            _sexp(
                                _ident('append'),
                                _literal(TokenKinds.STRING, 'no '),
                                _ident('cmd')
                            )
                        )
                    ),
                    _sexp(
                        _ident('for-each'),
                        _ident('cmd'),
                        _ident('fixes'),
                        _sexp(
                            _ident('exec-cmd'),
                            _ident('cmd')
                        )
                    )
                ),
            ),
        ]

        self.maxDiff = None
        self.assertEqual(expected_ast, parsed)

    @staticmethod
    def _tokeniser(*args) -> renderscript.parsing.tokeniser.FixedTokeniser:
        return renderscript.parsing.tokeniser.FixedTokeniser([
            _token(kind, value)
            for kind, value in args
        ])


def _token(kind: TokenKinds, value: str, start_position: typing.Optional[SourcePosition] = None,
           end_position: typing.Optional[SourcePosition] = None) -> Token:
    return Token(
        kind,
        value,
        typing.cast(SourcePosition, start_position),
        typing.cast(SourcePosition, end_position)
    )
