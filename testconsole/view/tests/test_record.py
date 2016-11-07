from six import b

from testtools.matchers import (
    Contains,
    Not,
)

from testconsole.testtools import (
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
        self.repository.add_record(TestRecord.create("foo", status=INPROGRESS))
        canvas = self.record.render((50,))
        self.assertThat(canvas.text[0], Contains(b("foo")))

    def test_render_status_success(self):
        """
        When a test moves to a state that is not INPROGRESS, the box title
        stays the same.
        """
        self.repository.add_record(TestRecord.create("foo", status=SUCCESS))
        canvas = self.record.render((50,))
        self.assertThat(canvas.text[0], Not(Contains(b("foo"))))
