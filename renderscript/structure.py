from dataclasses import dataclass
import typing


@dataclass(frozen=True)
class Node:
    pass


@dataclass(frozen=True)
class Comment(Node):
    text: str


@dataclass(frozen=True)
class Do(Node):
    children: typing.List[Node]


@dataclass(frozen=True)
class Bool(Node):
    value: bool


@dataclass(frozen=True)
class Number(Node):
    value: float


@dataclass(frozen=True)
class String(Node):
    value: str


@dataclass(frozen=True)
class List(Node):
    values: typing.List[Node]


@dataclass(frozen=True)
class MakeMap(Node):
    entries: typing.List[typing.Tuple[Node, Node]]


@dataclass(frozen=True)
class Identifier(Node):
    label: str


@dataclass(frozen=True)
class If(Node):
    condition: Node
    true: Node
    false: Node


@dataclass(frozen=True)
class Let(Node):
    name: Identifier
    expression: Node


@dataclass(frozen=True)
class ForEach(Node):
    value_name: Identifier
    collection: Node
    body: Node


@dataclass(frozen=True)
class Call(Node):
    target: Identifier
    arguments: typing.List[Node]
