import typing


from .tokeniser import TokenKinds
from .parser import AstNode
from .. import structure


def build(ast: typing.List[AstNode]) -> typing.List[structure.Node]:
    return [
        build_node(ast_node) for ast_node in ast
    ]


def build_node(ast: AstNode) -> structure.Node:
    known_node_kinds = {
        TokenKinds.STRING: lambda node: structure.String(node.head.value),
        TokenKinds.NUMBER: lambda node: structure.Number(
            float(node.head.value) if '.' in node.head.value else int(node.head.value)
        ),
        TokenKinds.BOOL: lambda node: structure.Bool(True if node.head.value == 'true' else False),
        TokenKinds.IDENTIFIER: lambda node: structure.Identifier(node.head.value),
        TokenKinds.OPEN_PAREN: build_sexpression,
    }

    if ast.head.kind in known_node_kinds:
        return known_node_kinds[ast.head.kind](ast)

    raise Exception(f"unable to build interpreter node from ast node: {ast}")


def build_sexpression(ast: AstNode) -> structure.Node:
    language_functions = {
        'let': build_let,
        'if': build_if,
        'for-each': build_foreach,
        'list': build_list,
        'make-map': build_makemap,
        'do': build_do,
    }

    if len(ast.tail) < 1:
        raise Exception(f"unexpected empty s-expression at {ast.head.start_position}")
    fn_name_node = ast.tail[0]
    if fn_name_node.head.kind != TokenKinds.IDENTIFIER:
        raise Exception(f"expected s-expression to start with an identifier at {fn_name_node.head.start_position}")
    fn_name = fn_name_node.head.value

    if fn_name in language_functions:
        return language_functions[fn_name](ast)
    else:
        return structure.Call(structure.Identifier(fn_name), [
            build_node(node) for node in ast.tail[1:]
        ])


def build_let(ast: AstNode) -> structure.Let:
    if len(ast.tail) != 3:
        raise Exception(f"expected two values passed to let at {ast.head.start_position}")
    identifier_node = ast.tail[1]
    expression_node = ast.tail[2]
    if identifier_node.head.kind != TokenKinds.IDENTIFIER:
        raise Exception(f"expected identifier as name of variable to declare at {identifier_node.head.start_position}")
    return structure.Let(
        structure.Identifier(identifier_node.head.value),
        build_node(expression_node)
    )


def build_if(ast: AstNode) -> structure.If:
    if len(ast.tail) != 4:
        raise Exception(f"expected three values passed to if at {ast.head.start_position}")
    condition_node = ast.tail[1]
    true_node = ast.tail[2]
    false_node = ast.tail[3]
    return structure.If(
        build_node(condition_node),
        build_node(true_node),
        build_node(false_node),
    )


def build_foreach(ast: AstNode) -> structure.ForEach:
    if len(ast.tail) != 4:
        raise Exception(f"expected three values passed to for-each at {ast.head.start_position}")
    label_node = ast.tail[1]
    if label_node.head.kind != TokenKinds.IDENTIFIER:
        raise Exception(f"expected identifier as name of iteration variable at {label_node.head.start_position}")
    label_name = label_node.head.value
    list_node = ast.tail[2]
    body_node = ast.tail[3]
    return structure.ForEach(
        structure.Identifier(label_name),
        build_node(list_node),
        build_node(body_node)
    )


def build_list(ast: AstNode) -> structure.List:
    return structure.List([
        build_node(node) for node in ast.tail[1:]
    ])


def build_do(ast: AstNode) -> structure.Do:
    return structure.Do([
        build_node(node) for node in ast.tail[1:]
    ])


def build_makemap(ast: AstNode) -> structure.MakeMap:
    args = ast.tail[1:]
    if len(args) % 2 != 0:
        raise Exception(f"expected even number of arguments to make-map at {ast.head.start_position}")
    entries = []
    for index in range(0, len(args), 2):
        entries.append(
            (build_node(args[index]), build_node(args[index + 1]))
        )
    return structure.MakeMap(entries)
