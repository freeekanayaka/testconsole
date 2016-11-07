import time

from logging import (
    LogRecord,
    INFO,
)
from systemfixtures import FakeTime

from testtools import TestCase

from testconsole.urwid import Logger


class LoggerTest(TestCase):

    def setUp(self):
        super(LoggerTest, self).setUp()
        self.time = self.useFixture(FakeTime())
        self.time.set(seconds=1478383023.22)
        self.logger = Logger()

    def test_render_one(self):
        """
        If there's only one record, no new line gets inserted.
        """
        self.logger.emit(LogRecord("root", INFO, None, None, "hi", None, None))
        self.assertEqual(
            "2016-11-05 21:57:03,220 [root:INFO] hi", self.logger.text)

    def test_render_many(self):
        """
        If there's more than one record, they're separated by new lines.
        """
        self.logger.emit(LogRecord("root", INFO, None, None, "hi", None, None))
        self.logger.emit(LogRecord("root", INFO, None, None, "yo", None, None))
        self.assertEqual(
            ["2016-11-05 21:57:03,220 [root:INFO] hi",
             "2016-11-05 21:57:03,220 [root:INFO] yo"],
            self.logger.text.strip().split("\n"))

    def test_render_timestamp(self):
        """
        The timestamp is considered.
        """
        self.logger.emit(LogRecord("root", INFO, None, None, "hi", None, None))
        time.sleep(1)
        self.logger.emit(LogRecord("root", INFO, None, None, "hi", None, None))
        self.assertEqual(
            ["2016-11-05 21:57:03,220 [root:INFO] hi",
             "2016-11-05 21:57:04,220 [root:INFO] hi"],
            self.logger.text.strip().split("\n"))

    def test_render_max_lines(self):
        """
        If max_lines not None, records get truncated.
        """
        self.logger.max_records = 1
        self.logger.emit(LogRecord("root", INFO, None, None, "hi", None, None))
        self.logger.emit(LogRecord("root", INFO, None, None, "yo", None, None))
        self.assertEqual(
            "2016-11-05 21:57:03,220 [root:INFO] yo", self.logger.text)
