import logging

from testtools.testresult.real import STATES

from obsub import event

from testconsole.testtools import INPROGRESS


class Repository(object):
    """Hold information about a collection of test records."""

    def __init__(self):
        self._index = {}
        self._previous_status = {}
        self._counts = {state: 0 for state in STATES}

    def get_record(self, test_id):
        """Return the test case with the given ID."""
        return self._index.get(test_id)

    def add_record(self, record):
        """Add a new test record to the repository.

        If a test record with the same ID already exists, it will be silently
        overwritten.
        """
        logging.debug("Add test record '%s'", record.id)
        if record.id in self._index:
            logging.warning("Overwrite test record '%s'", record.id)
        self.update_record(record)

    def update_record(self, record):
        """Update the given record.

        :param record: A TestRecord that already exists in the repository.
        """
        self._index[record.id] = record

        if record.status:
            logging.debug("Counts: '%s' -> '%s'", record.id, record.status)
            previous_status = self._previous_status.get(record.id)
            if previous_status:
                self._counts[previous_status] -= 1
            self._previous_status[record.id] = record.status
            self._counts[record.status] += 1
            self.on_change_counts()

            if record.status == INPROGRESS and previous_status != INPROGRESS:
                self.on_change_inprogress_record(record)

        if record.details and record.eof:
            logging.debug("Got complete details for %s", record.last_file_name)
            last_details = record.details[record.last_file_name]
            self.on_change_details(record.last_file_name, last_details)

    def count_records(self, states=STATES):
        """
        Return the number of cases in the given states (default to all states).
        """
        return sum([
            self._counts[state] for state in self._counts if state in states])

    @event
    def on_change_counts(self):
        """Notifier triggering when status counts change."""

    @event
    def on_change_inprogress_record(self, record):
        """Notifier triggering when a new test gets started."""

    @event
    def on_change_details(self, file_name, details):
        """Notifier triggering when receiving all packets for a detail."""
