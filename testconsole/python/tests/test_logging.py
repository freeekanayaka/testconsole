from logging import (
    LogRecord,
    INFO,
)

from testtools import TestCase

from systemfixtures import FakeTime

from testconsole.python import MillisecondFormatter


class MillisecondFormatterTest(TestCase):

    def setUp(self):
        super(MillisecondFormatterTest, self).setUp()
        self.time = self.useFixture(FakeTime())
        self.time.set(seconds=1478383023.22)

    def test_default(self):
        record = LogRecord("root", INFO, None, None, "hi", None, None)
        formatter = MillisecondFormatter()
        self.assertEqual(
            "2016-11-05 21:57:03,220", formatter.formatTime(record))

    def test_with_datefmt(self):
        record = LogRecord("root", INFO, None, None, "hi", None, None)
        formatter = MillisecondFormatter()
        self.assertEqual(
            "21:57:03.220000",
            formatter.formatTime(record, datefmt="%H:%M:%S.%f"))
