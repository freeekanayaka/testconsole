from testconsole.testtools import InterimStreamToTestRecord
from testconsole.controller.protocol import SubunitProtocol


class Controller(object):
    """Controller reacting to subunit and UI events."""

    def __init__(self, watcher, repository):
        """
        :param watcher: A concrete :class:``AbstractWatcher`` to use for
            getting subunit bytes.
        :param repository: The :class:``Repository`` to use to hold information
            about test cases being run.
        """
        self._watcher = watcher
        self._repository = repository
        result = InterimStreamToTestRecord(self._on_record)
        result.startTestRun()
        self._protocol = SubunitProtocol(result)
        self._loop = None

    def attach(self, loop):
        """
        Attach the controller to the given main loop and start handling events.
        """
        self._loop = loop
        self._watcher.attach(self._loop, self._protocol)

    def _on_record(self, record):
        if not self._repository.get_record(record.id):
            self._repository.add_record(record)
        else:
            self._repository.update_record(record)
