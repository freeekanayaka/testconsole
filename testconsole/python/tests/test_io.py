import errno

from six import b

from testtools import TestCase

from testconsole.python import AsyncBytesIO


class AsyncBytesIOTest(TestCase):

    def setUp(self):
        super(AsyncBytesIOTest, self).setUp()
        self.buffer = AsyncBytesIO()

    def test_read(self):
        """
        Data is read normally if the underlying EOF is not reached.
        """
        self.buffer.write(b("foo"))
        self.buffer.seek(0)
        self.assertEqual(b("foo"), self.buffer.read(3))

    def test_read_egain(self):
        """
        If the underlying EOF is reached, but the ``eof`` instance attribute
        is set to ``False``, an error is raised.
        """
        error = self.assertRaises(OSError, self.buffer.read, 1)
        self.assertEqual(errno.EAGAIN, error.errno)

    def test_read_eof(self):
        """
        If the underlying EOF is reached, and the ``eof`` instance attribute
        is set to ``True``, an empty string is returned, signalling the EOF.
        """
        self.buffer.eof = True
        self.assertEqual(b(""), self.buffer.read(1))
