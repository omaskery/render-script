from .visitor import Visitor
from . import structure


class SexpVisitor(Visitor):

    def __init__(self):
        super().__init__(throw_on_unknown=True)
        self.auto_detect_accept_methods()

    def accept_do(self, do_node: structure.Do):
        return self._render_sexp('do', *do_node.children)

    def accept_bool(self, bool_node: structure.Bool):
        return "true" if bool_node.value else "false"

    def accept_number(self, number_node: structure.Number):
        return str(number_node.value)

    def accept_string(self, string_node: structure.String):
        return f'"{string_node.value}"'

    def accept_list(self, list_node: structure.List):
        return self._render_sexp('list', *list_node.values)

    def accept_map(self, map_node: structure.MakeMap):
        return self._render_sexp('make-map', *sum([
            [key, value]
            for key, value in map_node.entries.items()
        ], []))

    def accept_if(self, if_node: structure.If):
        return self._render_sexp('if', if_node.condition, if_node.true, if_node.false)

    def accept_identifier(self, identifier_node: structure.Identifier):
        return identifier_node.label

    def accept_let(self, let_node: structure.Let):
        return self._render_sexp('let', let_node.name, let_node.expression)

    def accept_foreach(self, foreach_node: structure.ForEach):
        return self._render_sexp('for-each', foreach_node.value_name, foreach_node.collection, foreach_node.body)

    def accept_comment(self, comment_node: structure.Comment):
        return f";{comment_node.text}"

    def accept_call(self, call_node: structure.Call):
        return self._render_sexp(call_node.target, *call_node.arguments)

    def _render_sexp(self, *values):
        def _render(value):
            if isinstance(value, str):
                return value
            else:
                return self.accept(value)
        return f"({' '.join(map(_render, values))})"

