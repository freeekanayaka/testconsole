from six import b

from datetime import datetime

from testtools.matchers import (
    Contains,
    Not,
)
from testtools.content_type import ContentType
from testtools.content import Content
from testtools.testresult.real import utc

from testconsole.testtools import (
    EXISTS,
    INPROGRESS,
    SUCCESS,
    TestRecord,
)
from testconsole.view import (
    ViewTest,
    Record,
)


class RecordTest(ViewTest):

    def setUp(self):
        super(RecordTest, self).setUp()
        self.record = Record(self.repository)

    def test_render_status_inprogress(self):
        """
        When a test moves to the INPROGRESS, the box title gets updated.
        """
        record = TestRecord.create("foo", status=EXISTS)
        self.repository.add_record(record)
        self.repository.update_record(record.set(status=INPROGRESS))
        canvas = self.record.render((50,))
        self.assertThat(canvas.text[0], Contains(b("foo")))

    def test_render_status_success(self):
        """
        When a test moves to a state that is not INPROGRESS, the box title
        stays the same.
        """
        record = TestRecord.create("foo", status=EXISTS)
        self.repository.add_record(record)
        self.repository.update_record(record.set(status=INPROGRESS))
        self.repository.update_record(record.set(status=SUCCESS))
        canvas = self.record.render((50,))
        self.assertThat(canvas.text[0], Contains(b("foo")))

    def test_render_log(self):
        """
        If the test has a log detail attached, it gets flushed to the
        text widget.
        """
        content_type = ContentType("text", "x-log")
        record = TestRecord.create("foo", status=EXISTS)
        self.repository.add_record(record)
        self.repository.update_record(record.set(status=INPROGRESS))
        record.status = None
        record.timestamps = (record.timestamps[0], datetime.now(utc))
        record.details["test.log"] = Content(content_type, lambda: [b("ugh")])
        self.repository.update_record(record)
        canvas = self.record.render((50,))
        self.assertThat(canvas.text[1], Contains(b("ugh")))

    def test_render_traceback(self):
        """
        If the test has a traceback detail attached, it gets flushed to the
        log widget.
        """
        content_type = ContentType("text", "x-traceback")
        record = TestRecord.create("foo", status=EXISTS)
        self.repository.add_record(record)
        self.repository.update_record(record.set(status=INPROGRESS))
        record.status = None
        record.timestamps = (record.timestamps[0], datetime.now(utc))
        record.details["traceback"] = Content(content_type, lambda: [b("ugh")])
        self.repository.update_record(record)
        canvas = self.record.render((50,))
        self.assertThat(canvas.text[1], Contains(b("ugh")))
