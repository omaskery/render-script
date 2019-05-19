import unittest


from renderscript.utils import make_default_interpreter, execute_script


class TestUtils(unittest.TestCase):

    def test_execution(self):
        interpreter = make_default_interpreter()

        result = execute_script("""
        (equals (length (list 1 2 3)) 3)
        """, interpreter)
        self.assertTrue(result)
