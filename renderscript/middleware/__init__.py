from ..sexp_renderer import SexpVisitor


class DebugMiddleware:

    def __init__(self):
        self._indent = 0
        self._sexp_renderer = SexpVisitor()

    def __call__(self, accept, visiting):
        indent = "|   " * self._indent
        print(f"{indent}interpreting: {self._sexp_renderer.accept(visiting)}")
        self._indent += 1
        result = accept(visiting)
        self._indent -= 1
        print(f"{indent}+-- {repr(result)}")
        return result
