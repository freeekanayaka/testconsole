import logging

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
        self._protocol = SubunitProtocol(self)
        self._loop = None

    def attach(self, loop):
        """
        Attach the controller to the given main loop and start handling events.
        """
        self._loop = loop
        self._watcher.attach(self._loop, self._protocol)

    def status(self, test_id=None, test_status=None, test_tags=None,
               runnable=True, file_name=None, file_bytes=None, eof=False,
               mime_type=None, route_code=None, timestamp=None):

        if test_status and not test_id:
            logging.warning(
                "Got packet with status '%s' and no test_id", test_status)

        elif test_id:
            if not self._repository.get_case(test_id):
                self._repository.add_case(test_id)
            self._repository.set_state(test_id, test_status)
