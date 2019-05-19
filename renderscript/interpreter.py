from .visitor import Visitor
from . import structure


class Interpreter(Visitor):

    def __init__(self, middleware=None):
        super().__init__(throw_on_unknown=True)
        self.auto_detect_accept_methods()
        self.variable_scopes = [{}]
        self.external_calls = {}
        self._middleware = middleware

    def accept(self, visiting):
        if self._middleware is not None:
            return self._middleware(super().accept, visiting)
        else:
            return super().accept(visiting)

    def register_external_call(self, name, callback):
        self.external_calls[name] = callback

    def set_middleware(self, middleware):
        self._middleware = middleware

    def _push_scope(self):
        self.variable_scopes.append({})

    def _pop_scope(self):
        self.variable_scopes.pop()

    def _lookup_variable(self, name):
        for scope in reversed(self.variable_scopes):
            if name in scope:
                return scope, scope[name]
        raise Exception(f"unknown variable '{name}'")

    def _create_variable(self, name, value):
        self.variable_scopes[-1][name] = value

    def accept_do(self, do_node: structure.Do):
        result = None
        for node in do_node.children:
            result = self.accept(node)
        return result

    def accept_bool(self, bool_node: structure.Bool):
        return bool_node.value

    def accept_number(self, number_node: structure.Number):
        return number_node.value

    def accept_string(self, string_node: structure.String):
        return string_node.value

    def accept_list(self, list_node: structure.List):
        return [
            self.accept(value) for value in list_node.values
        ]

    def accept_map(self, map_node: structure.MakeMap):
        return dict([
            (self.accept(key), self.accept(value))
            for key, value in map_node.entries
        ])

    def accept_if(self, if_node: structure.If):
        return self.accept(if_node.true) if self.accept(if_node.condition) else self.accept(if_node.false)

    def accept_identifier(self, identifier_node: structure.Identifier):
        return self._lookup_variable(identifier_node.label)[1]

    def accept_let(self, let_node: structure.Let):
        self._create_variable(
            let_node.name.label,
            self.accept(let_node.expression)
        )

    def accept_foreach(self, foreach_node: structure.ForEach):
        def _body(value):
            self._push_scope()
            self._create_variable(foreach_node.value_name.label, value)
            result = self.accept(foreach_node.body)
            self._pop_scope()
            return result

        return [
            _body(value) for value in self.accept(foreach_node.collection)
        ]

    def accept_comment(self, _comment_node: structure.Comment):
        return None

    def accept_call(self, call_node: structure.Call):
        external_fn = self.external_calls.get(call_node.target.label)
        if external_fn is not None:
            return external_fn(self.accept, call_node.target.label, *call_node.arguments)
        raise Exception(f"unknown function '{call_node.target.label}' (arguments: {call_node.arguments})")
