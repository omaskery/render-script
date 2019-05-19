from contextlib import contextmanager


from .visitor import Visitor
from . import structure


class MarkdownRenderer(Visitor):

    def __init__(self):
        super().__init__(throw_on_unknown=True)
        self.auto_detect_accept_methods()
        self.markdown_lines = []
        self.indentation = []
        self.active_lists = []
        self.external_calls = {}
        self.expression_visitor = ExpressionVisitor()

    def register_external_call(self, name, descriptor_fn):
        self.external_calls[name] = descriptor_fn

    def render(self, compiled_script):
        for node in compiled_script:
            self.accept(node)
            self.write_line()

    @property
    def markdown(self):
        return "\n".join(self.markdown_lines)

    def accept_do(self, do_node: structure.Do):
        with self._current_item_mgr("Perform the following steps:"):
            with self._unordered_list():
                for node in do_node.children:
                    self.accept(node)

    def accept_bool(self, bool_node: structure.Bool):
        raise NotImplemented()

    def accept_number(self, number_node: structure.Number):
        raise NotImplemented()

    def accept_string(self, string_node: structure.String):
        raise NotImplemented()

    def accept_list(self, list_node: structure.List):
        raise NotImplemented()

    def accept_map(self, map_node: structure.MakeMap):
        raise NotImplemented()

    def accept_if(self, if_node: structure.If):
        condition = self.expression_visitor.accept(if_node.condition)
        with self._current_item_mgr(f"If {condition}:"):
            with self._unordered_list():
                self.accept(if_node.true)
        self.write_line()
        with self._current_item_mgr("Otherwise:"):
            with self._unordered_list():
                self.accept(if_node.false)

    def accept_identifier(self, identifier_node: structure.Identifier):
        raise NotImplemented()

    def accept_let(self, let_node: structure.Let):
        var_name = self._inline_code(let_node.name.label)
        with self._current_item_mgr(f"To create the variable {var_name}:"):
            with self._unordered_list():
                self.accept(let_node.expression)

    def accept_foreach(self, foreach_node: structure.ForEach):
        item_var = self.expression_visitor.accept(foreach_node.value_name)
        collection_var = self.expression_visitor.accept(foreach_node.collection)
        with self._current_item_mgr(f"For each {item_var} in {collection_var}:"):
            with self._unordered_list():
                self.accept(foreach_node.body)

    def accept_comment(self, _comment_node: structure.Comment):
        raise NotImplemented()

    def accept_call(self, call_node: structure.Call):
        fn_name = call_node.target.label
        if fn_name not in self.external_calls:
            raise Exception(f"unable to describe unknown external call '{fn_name}'")

        descriptor_fn = self.external_calls[fn_name]
        descriptor_fn(self, call_node)

    def write_header(self, level, text):
        self.write_line('#' * level + ' ' + text)
        self.write_line()

    def write_line(self, text='', disable_blank_line_check=False):
        if '\n' in text:
            lines = text.splitlines()
            for line in lines:
                self.write_line(line, disable_blank_line_check=disable_blank_line_check)
        else:
            if not disable_blank_line_check and self.line_is_blank(text) and self.last_line_is_blank():
                return

            self.markdown_lines.append(self._make_line_prefix() + text)

    def last_line_is_blank(self):
        if len(self.markdown_lines) < 1:
            return False
        else:
            return self.line_is_blank(self.markdown_lines[-1])

    def _make_line_prefix(self):
        base_indentation = "".join(self.indentation)
        return base_indentation

    @property
    def _current_item_mgr(self):
        if len(self.active_lists) > 0:
            _, item_mgr = self.active_lists[-1]
            return item_mgr
        else:
            @contextmanager
            def _fake_item_mgr(first_line):
                self.write_line(first_line)
                try:
                    yield None
                finally:
                    pass
            return _fake_item_mgr

    @staticmethod
    def _inline_code(text):
        return f"`{text}`"

    def _code_block(self, language, code):
        self.write_line(f"```{language}")
        self.write_line(code, disable_blank_line_check=True)
        self.write_line(f"```")

    @contextmanager
    def _with_indent(self, indentation):
        self._indent(indentation)
        try:
            yield None
        finally:
            self._dedent()

    @contextmanager
    def _ordered_list(self):
        _item_context = self._begin_ordered_list()
        try:
            yield _item_context
        finally:
            self._end_list()

    @contextmanager
    def _unordered_list(self):
        _item_context = self._begin_unordered_list()
        try:
            yield _item_context
        finally:
            self._end_list()

    def _begin_ordered_list(self):
        return self._begin_list('1) ')

    def _begin_unordered_list(self):
        return self._begin_list('- ')

    def _begin_list(self, kind):
        @contextmanager
        def _item_context(first_line):
            self.write_line(kind + first_line)
            self._indent('  ')
            try:
                yield None
            finally:
                self._dedent()
        self.active_lists.append((kind, _item_context))
        return _item_context

    def _end_list(self):
        self.active_lists.pop()

    def _indent(self, indentation):
        self.indentation.append(indentation)

    def _dedent(self):
        self.indentation.pop()

    @staticmethod
    def line_is_blank(text):
        return text.strip() == ''


class ExpressionVisitor(Visitor):

    def __init__(self):
        super().__init__(throw_on_unknown=True)
        self.auto_detect_accept_methods()
        self.external_calls = {}

    def register_external_call(self, name, descriptor_fn):
        self.external_calls[name] = descriptor_fn

    def accept_bool(self, bool_node: structure.Bool):
        raise NotImplemented()

    def accept_number(self, number_node: structure.Number):
        return str(number_node.value)

    def accept_string(self, string_node: structure.String):
        raise NotImplemented()

    def accept_list(self, list_node: structure.List):
        raise NotImplemented()

    def accept_map(self, map_node: structure.MakeMap):
        raise NotImplemented()

    def accept_if(self, if_node: structure.If):
        raise NotImplemented()

    def accept_identifier(self, identifier_node: structure.Identifier):
        return f"`{identifier_node.label}`"

    def accept_call(self, call_node: structure.Call):
        fn_name = call_node.target.label
        if fn_name not in self.external_calls:
            raise Exception(f"unable to describe unknown external call '{fn_name}'")

        descriptor_fn = self.external_calls[fn_name]
        return descriptor_fn(self, call_node)
