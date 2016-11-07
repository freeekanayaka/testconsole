from six import b

from testtools import TestCase
from testtools.content import (
    ContentType,
    Content,
)
from fixtures import FakeLogger

from testconsole.testtools import TestRecord
from testconsole.testtools import (
    EXISTS,
    INPROGRESS,
)
from testconsole.model import Repository


class RepositoryTest(TestCase):

    def setUp(self):
        super(RepositoryTest, self).setUp()
        self.logger = self.useFixture(FakeLogger())
        self.repository = Repository()

    def test_add_record(self):
        """
        A new test record can be added to the repository.
        """
        self.repository.add_record(TestRecord.create("foo", status=EXISTS))
        record = self.repository.get_record("foo")
        self.assertEqual("foo", record.id)

    def test_add_record_skip_existing(self):
        """
        Adding a test record with the ID name of an existing one that had been
        added earlier skips the record entirely.
        """
        self.repository.add_record(TestRecord.create("foo", status=EXISTS))
        record = self.repository.get_record("foo")
        self.repository.add_record(TestRecord.create("foo", status=EXISTS))
        self.assertIs(record, self.repository.get_record("foo"))
        self.assertEqual(
            "Runnable test record 'foo' exists, skipping it\n",
            self.logger.output)

    def test_add_record_increase_count(self):
        """
        Adding a record record increases the count for its status.
        """
        self.repository.add_record(TestRecord.create("foo", status=EXISTS))
        self.assertEqual(1, self.repository.count_records(states=[EXISTS]))

    def test_add_non_runnable_record_does_not_increase_count(self):
        """
        If the record being added is not runnable, counts are not increased.
        """
        self.repository.add_record(
            TestRecord.create("foo", status=INPROGRESS, runnable=False))
        self.assertEqual(0, self.repository.count_records())

    def test_unknown_status(self):
        """
        If the record being added has an unknown status, a warning is logged.
        """
        self.repository.add_record(TestRecord.create("foo", status="foo"))
        self.assertEqual("Unknown status 'foo'\n", self.logger.output)

    def test_update_record_previous_status(self):
        """
        Setting a new status for a record, decreases the count of the previous
        status.
        """
        record = TestRecord.create("foo", status=EXISTS)
        self.repository.add_record(record)
        self.repository.update_record(record.set(status=INPROGRESS))
        self.assertEqual(0, self.repository.count_records(states=[EXISTS]))
        self.assertEqual(1, self.repository.count_records(states=[INPROGRESS]))

    def test_count_records(self):
        """
        It's possible to get the total or partial count of test records in a
        repository.
        """
        record1 = TestRecord.create("foo", status=EXISTS)
        record2 = TestRecord.create("bar", status=EXISTS)

        self.repository.add_record(record1)
        self.repository.add_record(record2)
        self.repository.update_record(record2.set(status=INPROGRESS))

        self.assertEqual(2, self.repository.count_records())
        self.assertEqual(1, self.repository.count_records(states=[EXISTS]))
        self.assertEqual(1, self.repository.count_records(states=[INPROGRESS]))

    def test_on_record_start(self):
        """
        The on_record_start callback is fired when a record transitions to the
        'inprogress' state for the first time.
        """
        records = []

        def callback(repository, record):
            records.append(record)

        record = TestRecord.create("bar", status=EXISTS)
        self.repository.add_record(record)
        self.repository.on_record_start += callback
        self.repository.update_record(record.set(status=INPROGRESS))

        self.assertEqual([record], records)

    def test_on_record_progress(self):
        """
        The on_record_progress callback is fired if an interim log detail is
        received.
        """
        records = []

        def callback(repository, record):
            records.append(record)

        record = TestRecord.create("bar", status=None)
        record.details["test.log"] = Content(
            ContentType("text", "x-log"), lambda: [b("hello")])

        self.repository.on_record_progress += callback
        self.repository.update_record(record)

        self.assertEqual([record], records)
