from renderscript.sexp_renderer import SexpVisitor
from renderscript.interpreter import Interpreter
from renderscript import structure as s
from renderscript.builtin_functions import register_builtins


from unittest.mock import MagicMock, call
import unittest


class TestExampleScript(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indent = 0
        self._sexp_renderer = SexpVisitor()

    def setUp(self):
        self.i = Interpreter()

        register_builtins(self.i)

        self.mock_exec_cmd = MagicMock()
        self.i.register_external_call('exec-cmd', self.mock_exec_cmd)

        self.script = s.Do([
            s.Let(
                s.Identifier('snmp_cmds'),
                s.Call(
                    s.Identifier('splitlines'), [
                        s.Call(
                            s.Identifier('exec-cmd'),
                            [s.String("sh | include snmpv[12]")]
                        ),
                    ]
                )
            ),
            s.If(
                s.Call(
                    s.Identifier('equals'), [
                        s.Call(
                            s.Identifier('length'),
                            [s.Identifier('snmp_cmds')]
                        ),
                        s.Number(0),
                    ]
                ),
                s.String('no issue'),
                s.Do([
                    s.Let(
                        s.Identifier('fixes'),
                        s.ForEach(
                            s.Identifier('cmd'),
                            s.Identifier('snmp_cmds'),
                            s.Call(
                                s.Identifier('append'), [
                                    s.String("no "),
                                    s.Identifier("cmd"),
                                ]
                            )
                        )
                    ),
                    s.ForEach(
                        s.Identifier("cmd"),
                        s.Identifier("fixes"),
                        s.Call(
                            s.Identifier('exec-cmd'),
                            [s.Identifier('cmd')]
                        )
                    ),
                    s.String('success')
                ])
            )
        ])

    def test_no_issue(self):
        self._mock_device_behaviour({
            'sh | include snmpv[12]': [],
        })
        result = self.i.accept(self.script)
        self.mock_exec_cmd.assert_called_with(self.i.accept, 'exec-cmd', s.String('sh | include snmpv[12]'))
        self.assertEqual('no issue', result)

    def test_success(self):
        self._mock_device_behaviour({
            'sh | include snmpv[12]': [
                "snmpv1 blah",
                "snmpv2 blahblah",
            ],
            "no snmpv1 blah": "ok",
            "no snmpv2 blahblah": "ok",
        })
        result = self.i.accept(self.script)
        self.mock_exec_cmd.assert_has_calls([
            call(self.i.accept, 'exec-cmd', s.String('sh | include snmpv[12]')),
            call(self.i.accept, 'exec-cmd', s.Identifier('cmd')),
            call(self.i.accept, 'exec-cmd', s.Identifier('cmd')),
        ])
        self.assertEqual('success', result)

    def _mock_device_behaviour(self, responses):
        def _behaviour(evaluate, _name, cmd):
            command = evaluate(cmd)
            mapping = responses.get(command)
            if mapping is None:
                return None
            if isinstance(mapping, str):
                result = mapping
            else:
                result = "\n".join(mapping)
            return result
        self.mock_exec_cmd.side_effect = _behaviour
