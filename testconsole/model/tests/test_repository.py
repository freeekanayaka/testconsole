from testtools import TestCase
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
        self.repository.add_record(TestRecord.create("foo"))
        record = self.repository.get_record("foo")
        self.assertEqual("foo", record.id)

    def test_add_record_override_existing(self):
        """
        Adding a test record with the ID name of an existing one that had been
        added earlier overwrites the existing one.
        """
        self.repository.add_record(TestRecord.create("foo", None))
        record = self.repository.get_record("foo")
        self.repository.add_record(TestRecord.create("foo", None))
        self.assertIsNot(record, self.repository.get_record("foo"))
        self.assertEqual("Overwrite test record 'foo'\n", self.logger.output)

    def test_add_record_increase_count(self):
        """
        Adding a record record increases the count for its status.
        """
        self.repository.add_record(TestRecord.create("foo", status=EXISTS))
        self.assertEqual(1, self.repository.count_records(states=[EXISTS]))

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
        record2 = TestRecord.create("bar", status=INPROGRESS)

        self.repository.add_record(record1)
        self.repository.add_record(record2)

        self.assertEqual(2, self.repository.count_records())
        self.assertEqual(1, self.repository.count_records(states=[EXISTS]))
        self.assertEqual(1, self.repository.count_records(states=[INPROGRESS]))
