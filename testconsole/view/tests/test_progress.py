from six import b

from testtools.matchers import Contains

from testconsole.testtools import (
    EXISTS,
    SUCCESS,
    INPROGRESS,
    TestRecord,
)
from testconsole.view import (
    ViewTest,
    Progress,
)


class ProgressTest(ViewTest):

    def setUp(self):
        super(ProgressTest, self).setUp()
        self.progress = Progress(self.repository)

    def test_render_no_cases(self):
        """
        If no test cases have been reported, the counters are all zeroed.
        """
        canvas = self.progress.render((50,))
        self.assertThat(
            canvas.text[0], Contains(b("total: 0 done: 0 left: 0 - 0 %")))

    def test_render_one(self):
        """
        If a single case gets added, the counters are updated accordingly.
        """
        self.repository.add_record(TestRecord.create("foo", status=EXISTS))
        canvas = self.progress.render((50,))
        self.assertThat(
            canvas.text[0], Contains(b("total: 1 done: 0 left: 1 - 0 %")))

    def test_render_progress(self):
        """
        When states get updated, the counters are refreshed accordingly.
        """
        record1 = TestRecord.create("foo", status=EXISTS)
        record2 = TestRecord.create("bar", status=EXISTS)
        self.repository.add_record(record1)
        self.repository.add_record(record2)
        self.repository.update_record(record1.set(status=INPROGRESS))
        self.repository.update_record(record1.set(status=SUCCESS))
        self.repository.update_record(record2.set(status=INPROGRESS))
        canvas = self.progress.render((50,))
        self.assertThat(
            canvas.text[0], Contains(b("total: 2 done: 1 left: 1 - 50 %")))
