import os
import errno

from testtools import TestCase
from testtools.testresult.doubles import StreamResult

from subunit.v2 import (
    StreamResultToBytes,
    ParseError,
)

from testconsole.python import AsyncStringIO
from testconsole.subunit import AsyncByteStreamToStreamResult


class AsyncByteStreamToStreamResultTest(TestCase):

    def setUp(self):
        super(AsyncByteStreamToStreamResultTest, self).setUp()
        self.result = StreamResult()
        self.stream = AsyncStringIO()
        self.encoder = StreamResultToBytes(self.stream.buffer)
        self.decoder = AsyncByteStreamToStreamResult(self.stream)
        self.decoder.run(self.result)

    def test_do_read_one(self):
        """
        If there's data for exactly one packet, the relevant event is fired.
        """
        self.encoder.status(test_id="foo", test_status="exists")
        self.stream.seek(0)
        self.decoder.do_read()
        [event] = self.result._events
        self.assertEqual(("status", "foo", "exists"), event[:3])

    def test_do_read_many(self):
        """
        If there's data for several packets, the all the relevant events
        are fired.
        """
        self.encoder.status(test_id="foo", test_status="exists")
        self.encoder.status(test_id="bar", test_status="exists")
        self.stream.seek(0)
        self.assertFalse(self.decoder.do_read())
        [event1, event2] = self.result._events
        self.assertEqual(("status", "foo", "exists"), event1[:3])
        self.assertEqual(("status", "bar", "exists"), event2[:3])

    def test_do_read_eof(self):
        """
        If the end of file is reached, the method returns True.
        """
        self.stream.eof = True
        self.assertTrue(self.decoder.do_read())

    def test_do_read_unexpected_os_error(self):
        """
        Unexpected errors are propagated.
        """
        def read(length):
            raise OSError(errno.ENOMEM, os.strerror(errno.ENOMEM))

        self.stream.read = read
        error = self.assertRaises(OSError, self.decoder.do_read)
        self.assertEqual(errno.ENOMEM, error.errno)

    def test_do_read_garbage(self):
        """
        If unexpected data is found, an error is raised.
        """
        self.stream.write("boom")
        self.stream.seek(0)
        error = self.assertRaises(ParseError, self.decoder.do_read)
        self.assertEqual("Invalid packet signature", str(error))
