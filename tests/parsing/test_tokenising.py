import unittest

import renderscript.parsing
from renderscript.parsing.source import SourcePosition
from renderscript.parsing.tokeniser import Token, TokenKinds
from tests.parsing.test_parser import _token


class TestTokeniser(unittest.TestCase):

    def test_tokeniser(self):
        test_cases = [
            ('', []),
            ('(', [
                Token(TokenKinds.OPEN_PAREN, '(', SourcePosition(1, 1), SourcePosition(1, 2))
            ]),
            (')', [
                Token(TokenKinds.CLOSE_PAREN, ')', SourcePosition(1, 1), SourcePosition(1, 2))
            ]),
            ('hello', [
                Token(TokenKinds.IDENTIFIER, 'hello', SourcePosition(1, 1), SourcePosition(1, 6))
            ]),
            ('true', [
                Token(TokenKinds.BOOL, 'true', SourcePosition(1, 1), SourcePosition(1, 5))
            ]),
            ('false', [
                Token(TokenKinds.BOOL, 'false', SourcePosition(1, 1), SourcePosition(1, 6))
            ]),
            ('1', [
                Token(TokenKinds.NUMBER, '1', SourcePosition(1, 1), SourcePosition(1, 2))
            ]),
            ('100', [
                Token(TokenKinds.NUMBER, '100', SourcePosition(1, 1), SourcePosition(1, 4))
            ]),
            ('100.', [
                Token(TokenKinds.NUMBER, '100.', SourcePosition(1, 1), SourcePosition(1, 5))
            ]),
            ('100.23', [
                Token(TokenKinds.NUMBER, '100.23', SourcePosition(1, 1), SourcePosition(1, 7))
            ]),
            ('"hello"', [
                Token(TokenKinds.STRING, 'hello', SourcePosition(1, 1), SourcePosition(1, 8))
            ]),
            (r'"hello\nthere"', [
                Token(TokenKinds.STRING, 'hello\nthere', SourcePosition(1, 1), SourcePosition(1, 15))
            ]),
            ('(this is a true "test" of 24.0 (different things) wow)', [
                Token(TokenKinds.OPEN_PAREN, '(', SourcePosition(1, 1), SourcePosition(1, 2)),
                Token(TokenKinds.IDENTIFIER, 'this', SourcePosition(1, 2), SourcePosition(1, 6)),
                Token(TokenKinds.IDENTIFIER, 'is', SourcePosition(1, 7), SourcePosition(1, 9)),
                Token(TokenKinds.IDENTIFIER, 'a', SourcePosition(1, 10), SourcePosition(1, 11)),
                Token(TokenKinds.BOOL, 'true', SourcePosition(1, 12), SourcePosition(1, 16)),
                Token(TokenKinds.STRING, 'test', SourcePosition(1, 17), SourcePosition(1, 23)),
                Token(TokenKinds.IDENTIFIER, 'of', SourcePosition(1, 24), SourcePosition(1, 26)),
                Token(TokenKinds.NUMBER, '24.0', SourcePosition(1, 27), SourcePosition(1, 31)),
                Token(TokenKinds.OPEN_PAREN, '(', SourcePosition(1, 32), SourcePosition(1, 33)),
                Token(TokenKinds.IDENTIFIER, 'different', SourcePosition(1, 33), SourcePosition(1, 42)),
                Token(TokenKinds.IDENTIFIER, 'things', SourcePosition(1, 43), SourcePosition(1, 49)),
                Token(TokenKinds.CLOSE_PAREN, ')', SourcePosition(1, 49), SourcePosition(1, 50)),
                Token(TokenKinds.IDENTIFIER, 'wow', SourcePosition(1, 51), SourcePosition(1, 54)),
                Token(TokenKinds.CLOSE_PAREN, ')', SourcePosition(1, 54), SourcePosition(1, 55)),
            ]),
        ]
        for source, expected_tokens in test_cases:
            with self.subTest(source):
                tokeniser = self._tokeniser(source)
                tokens = []
                while not tokeniser.is_eof():
                    tokens.append(tokeniser.get())
                self.assertListEqual(expected_tokens, tokens)

    @staticmethod
    def _tokeniser(text):
        return renderscript.parsing.tokeniser.Tokeniser(renderscript.parsing.source.StringSource(text))


class TestFixedTokeniser(unittest.TestCase):

    def test_peek(self):
        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([])
        self.assertIsNone(tokeniser.peek())

        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([
            _token(TokenKinds.NUMBER, '10'),
        ])
        self.assertEqual(_token(TokenKinds.NUMBER, '10'), tokeniser.peek())

    def test_get(self):
        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([])
        self.assertIsNone(tokeniser.get())

        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([
            _token(TokenKinds.NUMBER, '10'),
        ])
        self.assertEqual(_token(TokenKinds.NUMBER, '10'), tokeniser.get())

        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([
            _token(TokenKinds.NUMBER, '10'),
            _token(TokenKinds.STRING, 'hello'),
        ])
        self.assertEqual(_token(TokenKinds.NUMBER, '10'), tokeniser.get())
        self.assertEqual(_token(TokenKinds.STRING, 'hello'), tokeniser.peek())
        self.assertEqual(_token(TokenKinds.STRING, 'hello'), tokeniser.get())

    def test_tell(self):
        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([])
        self.assertEqual(SourcePosition(1, 1), tokeniser.tell())

        tokeniser = renderscript.parsing.tokeniser.FixedTokeniser([
            _token(TokenKinds.NUMBER, '10', SourcePosition(10, 11), SourcePosition(12, 13))
        ])
        self.assertEqual(SourcePosition(10, 11), tokeniser.tell())
        tokeniser.peek()
        self.assertEqual(SourcePosition(10, 11), tokeniser.tell())
        tokeniser.get()
        self.assertEqual(SourcePosition(12, 13), tokeniser.tell())
        tokeniser.peek()
        self.assertEqual(SourcePosition(12, 13), tokeniser.tell())
        tokeniser.get()
        self.assertEqual(SourcePosition(12, 13), tokeniser.tell())