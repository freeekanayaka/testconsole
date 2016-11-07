from datetime import datetime

from six import (
    BytesIO,
    b,
)

from subunit.v2 import StreamResultToBytes

from urwid import MainLoop

from testtools.testresult.real import utc

from testconsole.urwid import MemoryWatcher
from testconsole.testtools import (
    EXISTS,
    INPROGRESS,
)
from testconsole.view import (
    ViewTest,
    Console,
)
from testconsole.controller import Controller


class ControllerTest(ViewTest):

    def setUp(self):
        super(ControllerTest, self).setUp()
        stream = BytesIO()
        self.encoder = StreamResultToBytes(stream)
        self.loop = MainLoop(Console(self.repository))
        watcher = MemoryWatcher(stream)
        self.controller = Controller(watcher, self.repository)

    def test_attach(self):
        """
        When data is available for reading, the protocol gets notified.
        """
        self.encoder.status(test_id="foo", test_status=EXISTS)
        self.controller.attach(self.loop)
        record = self.repository.get_record("foo")
        self.assertEqual(1, self.repository.count_records())
        self.assertEqual("foo", record.id)
        self.assertEqual(EXISTS, record.status)

    def test_exists(self):
        """
        If packet with an existing test ID is received, the associated record
        gets updated.
        """
        self.encoder.status(test_id="foo", test_status=EXISTS)
        self.encoder.status(test_id="foo", test_status=INPROGRESS)
        self.controller.attach(self.loop)
        record = self.repository.get_record("foo")
        self.assertEqual(1, self.repository.count_records())
        self.assertEqual("foo", record.id)
        self.assertEqual(INPROGRESS, record.status)

    def test_exists_no_test_id(self):
        """
        If packet is received with test status ``exists`` but no test ID,
        it's simply discarded.
        """
        self.encoder.status(test_status="exists")
        self.controller.attach(self.loop)
        self.assertEqual(0, self.repository.count_records())

    def test_on_record_progress(self):
        """
        When all the packets for a details entry are received, an event is
        triggered by the repository.
        """
        records = []

        def on_record_progress(repository, record):
            records.append(record)

        self.repository.on_record_progress += on_record_progress
        self.encoder.status(test_id="foo", test_status=EXISTS)
        self.encoder.status(test_id="foo", test_status=INPROGRESS)
        self.encoder.status(
            test_id="foo", file_name="log", file_bytes=b("hello"),
            mime_type="text/x-log", timestamp=datetime.now(utc))
        self.controller.attach(self.loop)

        [record] = records
        self.assertEqual("hello", record.details["log"].as_text())
