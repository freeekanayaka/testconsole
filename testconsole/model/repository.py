import logging

from testtools.testresult.real import (
    FINAL_STATES,
    STATES,
)

from obsub import event

from testconsole.testtools import (
    INPROGRESS,
    EXISTS,
)


class Repository(object):
    """Hold information about a collection of test records."""

    def __init__(self):
        self._index = {}
        self._counts = {state: 0 for state in STATES - {None}}

    def get_record(self, test_id):
        """Return the test case with the given ID."""
        return self._index.get(test_id)

    def add_record(self, record):
        """Add a new test record to the repository.

        If a test record with the same ID already exists, it will be silently
        overwritten.
        """
        logging.debug("Add test record '%s'", record.id)
        if record.id in self._index and record.runnable:
            logging.warning(
                "Runnable test record '%s' exists, skipping it", record.id)
            return
        self.update_record(record)

    def update_record(self, record):
        """Update the given record.

        :param record: A TestRecord that already exists in the repository.
        """
        # TODO: The code below assumes that the packets in the subunit stream
        # are ordered in a deterministic and predictable way. E.g.:
        #
        # - the stream starts with a series of packets with status 'exists'
        #   each one associate with a test that is going to be run.
        #
        # - then test records sequentially transition from 'exists' to
        #   'inprogress' and then a final status (each transition happens
        #   only once and it's not interleaved with packets associated with
        #   other test cases)
        #
        # - x-log and x-traceback packets have no status and have a test ID
        #   that always matches the test ID of the currently 'inprogress' test
        #   case.
        #
        # These assumption are consistent with subunit.v2.StreamResultToBytes
        # and with subunitlogging.SubunitLoggingSuite.
        #
        # However at some point we might want to be more defensive, introducing
        # logic to spot and possibly resolve inconsistencies.
        self._index[record.id] = record

        if record.status:
            if record.status not in STATES:
                logging.warning("Unknown status '%s'", record.status)
                return

            # Runnable records are associated with actual test cases, so we
            # want to update the counts (non runnable records are typically
            # associated with fixtures and resources).
            if record.runnable:
                previous_status = self._get_previous_status(record.status)
                if previous_status:
                    self._counts[previous_status] -= 1
                    assert self._counts[previous_status] >= 0
                self._counts[record.status] += 1
                self.on_counts_change()

            if record.status == INPROGRESS:
                logging.debug("Start: '%s'", record.id)
                self.on_record_start(record)
            elif record.status in FINAL_STATES - {EXISTS}:
                logging.debug("Finish: '%s' -> '%s'", record.id, record.status)

        elif record.details:
            logging.debug("Record '%s' has new progress data", record.id)
            self.on_record_progress(record)

    def count_records(self, states=STATES):
        """Return the number of runnable records in the given states.

        The default is to return the count of all runnable records (i.e. in
        all states).
        """
        return sum([
            self._counts[state] for state in self._counts if state in states])

    @event
    def on_counts_change(self):
        """Notifier triggering when status counts change."""

    @event
    def on_record_start(self, record):
        """Notifier triggering when a new test gets started."""

    @event
    def on_record_progress(self, record):
        """Notifier triggering when receiving all packets for a detail."""

    def _get_previous_status(self, status):
        if status == EXISTS:
            return None
        elif status == INPROGRESS:
            return EXISTS
        elif status in FINAL_STATES - {EXISTS}:
            return INPROGRESS
