import unittest


from renderscript.utils import compile_script
from renderscript.render import MarkdownRenderer
from renderscript import structure


class TestMarkdownRenderer(unittest.TestCase):

    @unittest.skip("unimplemented while still prototyping approach")
    def test_rendering(self):
        test_cases = [
            (
                "",
                """"""
            ),
        ]
        for script, markdown in test_cases:
            with self.subTest(script):
                compiled_script = compile_script(script)
                renderer = MarkdownRenderer()
                renderer.render(compiled_script)
                self.assertEqual(markdown, renderer.markdown, "output markdown should match expected markdown")

    @unittest.skip("only used for prototyping locally")
    def test_rendering_prototype(self):
        source = """
(let snmp_cmds
    (splitlines
        (exec-cmd "sh | include snmpv[12]")))

(if (equals (length snmp_cmds) 0)
    (report "no-issue")
    (do
        (let fixes
            (for-each cmd snmp_cmds
                (append "no " cmd)))
        (for-each cmd fixes
            (exec-cmd cmd))
        (report "success")))
        """

        expected_markdown = ""

        compiled_script = compile_script(source)
        renderer = MarkdownRenderer()

        def _describe_splitlines(md, call_node: structure.Call):
            md.accept(call_node.arguments[0])
            with md._current_item_mgr(f"Then, split the result into a list of lines"):
                pass
        renderer.register_external_call('splitlines', _describe_splitlines)

        def _describe_exec_cmd(md, call_node: structure.Call):
            if isinstance(call_node.arguments[0], structure.String):
                with md._current_item_mgr(f"Execute the command:"):
                    md._code_block('bash', call_node.arguments[0].value)
            else:
                expression = md.expression_visitor.accept(call_node.arguments[0])
                with md._current_item_mgr(f"Then execute the resulting command: {expression}"):
                    pass
        renderer.register_external_call('exec-cmd', _describe_exec_cmd)

        def _describe_append(md, call_node: structure.Call):
            def _resolve_argument(arg):
                if isinstance(arg, structure.String):
                    return f"`{repr(arg.value)}`"
                else:
                    return md.expression_visitor.accept(arg)
            resolved = [_resolve_argument(arg) for arg in call_node.arguments]
            if len(resolved) == 2:
                with md._current_item_mgr(f"Append {resolved[0]} to {resolved[1]}"):
                    pass
        renderer.register_external_call('append', _describe_append)

        def _describe_report(md, call_node: structure.Call):
            if isinstance(call_node.arguments[0], structure.String):
                if call_node.arguments[0].value == "success":
                    text = "Report successfully remediated the issue"
                else:
                    text = "Report no issue detected to remediate"
                with md._current_item_mgr(text):
                    pass
            else:
                md.expression_visitor.accept(call_node.arguments[0])
                with md._current_item_mgr(f"Then report the result as the outcome of the remediation process"):
                    pass
        renderer.register_external_call('report', _describe_report)

        def _describe_equals_expression(exp, call_node: structure.Call):
            return f"{exp.accept(call_node.arguments[0])} is equal to {exp.accept(call_node.arguments[1])}"
        renderer.expression_visitor.register_external_call('equals', _describe_equals_expression)

        def _describe_length_expression(exp, call_node: structure.Call):
            return f"length of {exp.accept(call_node.arguments[0])}"
        renderer.expression_visitor.register_external_call('length', _describe_length_expression)

        renderer.render(compiled_script)

        with open('../test-outputs/example.md', 'w') as output:
            output.write(renderer.markdown)

        self.maxDiff = None
        self.assertEqual(expected_markdown, renderer.markdown)
