import enum
import re
import string
import typing
from dataclasses import dataclass

from renderscript.parsing.source import SourcePosition


@enum.unique
class TokenKinds(enum.Enum):
    OPEN_PAREN = enum.auto()
    CLOSE_PAREN = enum.auto()
    NUMBER = enum.auto()
    STRING = enum.auto()
    BOOL = enum.auto()
    IDENTIFIER = enum.auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKinds
    value: str
    start_position: SourcePosition
    end_position: SourcePosition

    def __str__(self):
        result = f"Token(kind={self.kind.name} value={repr(self.value)}"
        if self.start_position is not None:
            result += f" start={self.start_position}"
        if self.end_position is not None:
            result += f" end={self.end_position}"
        result += ")"
        return result

    def __repr__(self):
        return str(self)


class ITokeniser:

    def peek(self) -> typing.Optional[Token]:
        pass

    def get(self) -> typing.Optional[Token]:
        pass

    def is_eof(self) -> bool:
        pass

    def tell(self) -> SourcePosition:
        pass


class Tokeniser(ITokeniser):

    def __init__(self, source):
        self.source = source
        self.next_token = None

    def peek(self):
        self._cache_next_token()
        return self.next_token

    def get(self):
        result = self.peek()
        self.next_token = None
        return result

    def is_eof(self):
        self._cache_next_token()
        return self.next_token is None

    def tell(self):
        return self.source.tell()

    def _cache_next_token(self):
        if self.next_token is not None:
            return

        self._skip_whitespace()

        start_position = self.source.tell()
        next_char = self.source.peek()
        if next_char is None:
            return

        if next_char == '(':
            kind = TokenKinds.OPEN_PAREN
            value = self.source.get()
        elif next_char == ')':
            kind = TokenKinds.CLOSE_PAREN
            value = self.source.get()
        elif next_char == '"':
            kind = TokenKinds.STRING
            value = self._consume_string()
        elif next_char in string.digits:
            kind = TokenKinds.NUMBER
            value = self._consume_while_matches(r'\d+(\.\d*)?')
        else:
            kind = TokenKinds.IDENTIFIER
            value = self._consume_while_matches(r'[^\s()]+')
            if value in ('true', 'false'):
                kind = TokenKinds.BOOL

        end_position = self.source.tell()

        self.next_token = Token(kind, value, start_position, end_position)

    def _skip_whitespace(self):
        while not self.source.is_eof() and self.source.peek() in string.whitespace:
            self.source.get()

    def _consume_string(self):
        known_escapes = {
            't': '\t',
            'n': '\n',
            'r': '\r',
            'a': '\a',
            'f': '\f',
            '0': '\0',
            '\\': '\\',
        }
        text = ""
        if self.source.peek() != '"':
            raise Exception(f"cannot consume a string: expected initial '\"' at {self.source.tell()}")
        self.source.get()
        escaped = False
        while not self.source.is_eof():
            next_char = self.source.get()
            if not escaped and next_char == '"':
                break
            elif not escaped and next_char != '\\':
                text += next_char
            elif not escaped and next_char == '\\':
                escaped = True
            elif escaped:
                text += known_escapes[next_char]
                escaped = False
        return text

    def _consume_while_matches(self, pattern):
        regex = re.compile(pattern)
        consumed = ''
        while not self.source.is_eof():
            consumed += self.source.peek()
            if regex.fullmatch(consumed):
                self.source.get()
            else:
                consumed = consumed[:-1]
                break
        return consumed


class FixedTokeniser(ITokeniser):

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        if self.is_eof():
            return None
        return self.tokens[self.index]

    def get(self):
        result = self.peek()
        if result is not None:
            self.index += 1
        return result

    def is_eof(self):
        return self.index >= len(self.tokens)

    def tell(self):
        if not self.is_eof():
            return self.peek().start_position
        elif len(self.tokens) > 0:
            return self.tokens[-1].end_position
        else:
            return SourcePosition(1, 1)