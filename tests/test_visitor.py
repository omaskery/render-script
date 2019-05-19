from unittest.mock import MagicMock
import unittest

from renderscript.visitor import Visitor


class VisitorTests(unittest.TestCase):

    @staticmethod
    def test_visit():
        visitor = Visitor()

        callback = MagicMock()

        def handles_integer(a: int):
            callback(a)

        visitor.register_accept_method(handles_integer)

        visitor.accept(10)
        callback.assert_called_with(10)

    @staticmethod
    def test_multiple_visit_types():
        visitor = Visitor()

        callback = MagicMock()

        def handles_integer(a: int):
            callback(a, "integer")

        def handles_string(a: str):
            callback(a, "string")

        visitor.register_accept_method(handles_integer)
        visitor.register_accept_method(handles_string)

        visitor.accept("hello")
        callback.assert_called_with("hello", "string")

        visitor.accept(24)
        callback.assert_called_with(24, "integer")

    def test_inherited_visitor(self):
        class MyVisitor(Visitor):

            def __init__(self):
                super().__init__()
                self.auto_detect_accept_methods()
                self.visit_result = None

            def accept_int(self, value: int):
                self.visit_result = (value, 'int')

            def accept_str(self, value: str):
                self.visit_result = (value, 'str')

            def accept_other(self, visitable):
                self.visit_result = (visitable, None)

        visitor = MyVisitor()

        self.assertIsNone(visitor.visit_result)
        visitor.accept(24)
        self.assertEqual((24, 'int'), visitor.visit_result)
        visitor.accept("hello")
        self.assertEqual(("hello", 'str'), visitor.visit_result)
        visitor.accept(2.8)
        self.assertEqual((2.8, None), visitor.visit_result)

    def test_visitor_throws_on_unknown(self):
        visitor = Visitor(throw_on_unknown=True)

        with self.assertRaises(Exception) as cm:
            visitor.accept(10)

        self.assertEqual(("no accept function to handle visitor of type int",), cm.exception.args)

