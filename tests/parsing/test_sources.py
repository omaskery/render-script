import unittest

import renderscript.parsing


class TestStringSource(unittest.TestCase):

    def test_peek(self):
        source = self._source('')
        self.assertIsNone(source.peek())
        source = self._source('h')
        self.assertEqual('h', source.peek())
        source = self._source('hello')
        self.assertEqual('h', source.peek())

    def test_get(self):
        source = self._source('')
        self.assertIsNone(source.get())
        source = self._source('h')
        self.assertEqual('h', source.get())
        source = self._source('hello')
        self.assertEqual('h', source.get())
        self.assertEqual('e', source.get())
        self.assertEqual('l', source.get())
        self.assertEqual('l', source.get())
        self.assertEqual('o', source.get())
        self.assertIsNone(source.get())

    def test_get_then_peek(self):
        source = self._source('hello')
        self.assertEqual('h', source.peek())
        self.assertEqual('h', source.get())
        self.assertEqual('e', source.peek())
        self.assertEqual('e', source.get())
        self.assertEqual('l', source.peek())
        self.assertEqual('l', source.get())
        self.assertEqual('l', source.peek())
        self.assertEqual('l', source.get())
        self.assertEqual('o', source.peek())
        self.assertEqual('o', source.get())
        self.assertIsNone(source.peek())
        self.assertIsNone(source.get())

    def test_is_eof(self):
        source = self._source('')
        self.assertTrue(source.is_eof())
        source = self._source('h')
        self.assertFalse(source.is_eof())
        source = self._source('h')
        source.get()
        self.assertTrue(source.is_eof())
        source = self._source('hello')
        source.get()
        self.assertFalse(source.is_eof())
        source.get()
        self.assertFalse(source.is_eof())
        source.get()
        self.assertFalse(source.is_eof())
        source.get()
        self.assertFalse(source.is_eof())
        source.get()
        self.assertTrue(source.is_eof())

    def test_tell_not_affected_by_peek(self):
        source = self._source('hello')
        source.peek()
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 1), source.tell())

        source = self._source('\nthere')
        source.peek()
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 1), source.tell())

    def test_tell(self):
        source = self._source('')
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 1), source.tell())

        source = self._source('hello')
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 1), source.tell())
        source.get()
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 2), source.tell())
        source.get()
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 3), source.tell())
        source.get()
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 4), source.tell())

    def test_tell_handles_newlines(self):
        source = self._source('\n')
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 1), source.tell())
        source.get()
        self.assertEqual(renderscript.parsing.source.SourcePosition(2, 1), source.tell())

        source = self._source('hello\nthere')
        self.assertEqual(renderscript.parsing.source.SourcePosition(1, 1), source.tell())
        source.get()
        source.get()
        source.get()
        source.get()
        source.get()
        source.get()
        self.assertEqual(renderscript.parsing.source.SourcePosition(2, 1), source.tell())

    @staticmethod
    def _source(text):
        return renderscript.parsing.source.StringSource(text)