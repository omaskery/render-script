import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePosition:
    line: int
    column: int

    def next_column(self):
        return SourcePosition(self.line, self.column + 1)

    def next_line(self):
        return SourcePosition(self.line + 1, 1)

    def __str__(self):
        return f"{self.line}:{self.column}"


class Source:

    def peek(self) -> typing.Optional[str]:
        pass

    def get(self) -> typing.Optional[str]:
        pass

    def is_eof(self) -> bool:
        pass

    def tell(self) -> SourcePosition:
        pass


class StringSource(Source):

    def __init__(self, text):
        self.text = text
        self.index = 0
        self.source_position = SourcePosition(1, 1)

    def peek(self) -> typing.Optional[str]:
        if self.is_eof():
            return None
        return self.text[self.index]

    def get(self) -> typing.Optional[str]:
        result = self.peek()
        if result is not None:
            self.index += 1
            if result == '\n':
                self.source_position = self.source_position.next_line()
            else:
                self.source_position = self.source_position.next_column()
        return result

    def is_eof(self) -> bool:
        return self.index >= len(self.text)

    def tell(self) -> SourcePosition:
        return self.source_position