from testtools import TestCase
from fixtures import FakeLogger

from testconsole.model import (
    EXISTS,
    SUCCESS,
    INPROGRESS,
    Repository,
)


class RepositoryTest(TestCase):

    def setUp(self):
        super(RepositoryTest, self).setUp()
        self.logger = self.useFixture(FakeLogger())
        self.repository = Repository()

    def test_add_case(self):
        """
        A new test case can be added to the repository.
        """
        self.repository.add_case("foo")
        case = self.repository.get_case("foo")
        self.assertEqual("foo", case.id)

    def test_add_case_override_existing(self):
        """
        Adding a test case with the same name of an existing one that had been
        added earlier overwrites the existing one.
        """
        self.repository.add_case("foo")
        case = self.repository.get_case("foo")
        self.repository.add_case("foo")
        self.assertIsNot(case, self.repository.get_case("foo"))
        self.assertEqual("Overwrite test case 'foo'\n", self.logger.output)

    def test_set_state(self):
        """
        Setting the state of a case increases the count for that case.
        """
        self.repository.add_case("foo")
        self.repository.set_state("foo", EXISTS)
        self.assertEqual(1, self.repository.count_cases(states=[EXISTS]))

    def test_set_state_previous_state(self):
        """
        Setting a new state of a test, decreases the count of the previous
        state.
        """
        self.repository.add_case("foo")
        self.repository.set_state("foo", EXISTS)
        self.repository.set_state("foo", INPROGRESS)
        self.assertEqual(0, self.repository.count_cases(states=[EXISTS]))
        self.assertEqual(1, self.repository.count_cases(states=[INPROGRESS]))

    def test_count_cases(self):
        """
        It's possible to get the total or partial count of test cases in a
        repository.
        """
        self.repository.add_case("foo")
        self.repository.add_case("bar")
        self.repository.set_state("foo", EXISTS)
        self.repository.set_state("bar", INPROGRESS)
        self.assertEqual(2, self.repository.count_cases())
        self.assertEqual(1, self.repository.count_cases(states=[EXISTS]))
        self.assertEqual(1, self.repository.count_cases(states=[INPROGRESS]))
