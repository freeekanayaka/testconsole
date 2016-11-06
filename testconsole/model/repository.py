import logging

from testconsole.python import Undef
from testtools.testresult.real import STATES

from obsub import event

from testconsole.model.case import Case


class Repository(object):
    """Hold information about a collection of tests."""

    def __init__(self):
        self._tests = []
        self._index = {}
        self._done = 0
        self._counts = {state: 0 for state in STATES}

    def get_case(self, test_id):
        """Return the test case with the given ID."""
        return self._index.get(test_id)

    @event
    def add_case(self, test_id):
        """Add a new test case to the repository.

        If a test case with the same ID already exists, it will be silently
        overwritten.
        """
        logging.debug("Add test case '%s'", test_id)
        if test_id in self._index:
            logging.warning("Overwrite test case '%s'", test_id)
        case = Case(test_id)
        self._tests.append(case)
        self._index[test_id] = case
        return case

    @event
    def set_state(self, test_id, test_status):
        """Set the state of test case.

        :param test_id: The ID of a previously added test case.
        :param test_status: A valid state from ``STATES``.
        """
        logging.debug("Set state of '%s' to '%s'", test_id, test_status)
        case = self.get_case(test_id)
        if case.state is not Undef:
            self._counts[case.state] -= 1

        case.state = test_status

        self._counts[case.state] += 1

    def count_cases(self, states=STATES):
        """
        Return the number of cases in the given states (default to all states).
        """
        return sum([
            self._counts[state] for state in self._counts if state in states])
