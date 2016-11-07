from six import BytesIO

from subunit.v2 import StreamResultToBytes

from urwid import MainLoop

from testconsole.urwid import MemoryWatcher
from testconsole.model import EXISTS
from testconsole.view import (
    ViewTest,
    Console,
)
from testconsole.controller import Controller


class ControllerTest(ViewTest):

    def setUp(self):
        super(ControllerTest, self).setUp()
        stream = BytesIO()
        self.encoder = StreamResultToBytes(stream)
        self.loop = MainLoop(Console(self.repository))
        watcher = MemoryWatcher(stream)
        self.controller = Controller(watcher, self.repository)

    def test_attach(self):
        """
        When data is available for reading, the protocol gets notified.
        """
        self.encoder.status(test_id="foo", test_status=EXISTS)
        self.controller.attach(self.loop)
        case = self.repository.get_case("foo")
        self.assertEqual(1, self.repository.count_cases())
        self.assertEqual("foo", case.id)
        self.assertEqual(EXISTS, case.state)

    def test_exists_no_test_id(self):
        """
        If packet is received with test status ``exists`` but no test ID,
        it's simply discarded.
        """
        self.encoder.status(test_status="exists")
        self.controller.attach(self.loop)
        self.assertEqual(0, self.repository.count_cases())
        self.assertEqual(
            "Got packet with status 'exists' and no test_id\n",
            self.logger.output)
