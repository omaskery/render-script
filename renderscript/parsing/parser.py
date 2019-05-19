from dataclasses import dataclass
import typing

from renderscript.parsing.tokeniser import TokenKinds, Token, ITokeniser


@dataclass(frozen=True)
class AstNode:
    head: Token
    tail: typing.List['AstNode']


def parse(tokeniser: ITokeniser) -> typing.List[AstNode]:
    expressions = []
    while not tokeniser.is_eof():
        expressions.append(parse_expression(tokeniser))
    return expressions


def parse_expression(tokeniser: ITokeniser) -> AstNode:
    head = expect_token(tokeniser, TokenKinds.OPEN_PAREN)
    tail = []
    while peek_any_token(tokeniser).kind != TokenKinds.CLOSE_PAREN:
        tail.append(parse_atom(tokeniser))
    expect_token(tokeniser, TokenKinds.CLOSE_PAREN)
    return AstNode(head, tail)


def parse_atom(tokeniser: ITokeniser) -> AstNode:
    peek = tokeniser.peek()
    if peek.kind in (TokenKinds.IDENTIFIER, TokenKinds.NUMBER, TokenKinds.STRING, TokenKinds.BOOL):
        return AstNode(tokeniser.get(), [])
    elif peek.kind == TokenKinds.OPEN_PAREN:
        return parse_expression(tokeniser)
    else:
        raise Exception(f"unexpected token {peek}")


def peek_any_token(tokeniser: ITokeniser) -> Token:
    position = tokeniser.tell()
    next_token = tokeniser.peek()
    if next_token is None:
        raise Exception(f"unexpected end of stream at {position}")
    return next_token


def expect_token(tokeniser: ITokeniser, kind: TokenKinds) -> Token:
    position = tokeniser.tell()
    token = tokeniser.get()
    if token.kind != kind:
        raise Exception(f"expected token of kind '{kind}' at {position}")
    return token
