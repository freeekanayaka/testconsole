from six import b

from testtools import TestCase

from testconsole.testtools import (
    EXISTS,
    InterimStreamToTestRecord,
)


class InterimStreamToTestRecordTest(TestCase):

    def test_status(self):
        """
        The on_test callback gets fired also on packets with an interim status,
        and its 'interim' keyword argument is set to True.
        """
        records = []
        result = InterimStreamToTestRecord(records.append)
        result.startTestRun()
        result.status(test_id="foo", test_status=EXISTS)
        result.status(
            test_id="foo", file_name="test.log", file_bytes=b("hello"),
            mime_type="text/x-log")
        [_, record] = records
        self.assertIsNone(record.status)
        self.assertTrue(record.runnable)
        self.assertEqual("hello", record.details["test.log"].as_text())
