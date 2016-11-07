from testtools import TestCase

from fixtures import (
    FakeLogger,
    TempDir,
)

from systemfixtures import FakeProcesses

from urwid import MainLoop

from testconsole.command import main


class FakeLoop(MainLoop):

    def run(self):
        pass


class MainTest(TestCase):

    def setUp(self):
        super(MainTest, self).setUp()
        self.logger = self.useFixture(FakeLogger())

    def test_file_watcher(self):
        """If a filename is given, the stream source will be a file watcher."""

        filename = self.useFixture(TempDir()).join("data.subunit")
        with open(filename, "w") as fd:
            fd.write("")

        argv = ["testconsole", "-d", "-f", filename]
        main(argv=argv, loop_factory=FakeLoop)
        self.assertEqual("Start main loop\n", self.logger.output)

    def test_process_watcher(self):
        """
        If a command is given, the stream source will be a process watcher.
        """
        processes = self.useFixture(FakeProcesses())
        processes.add(lambda *args, **kwargs: {}, "foo")
        argv = ["testconsole", "-d", "-c", "foo"]
        main(argv=argv, loop_factory=FakeLoop)
        self.assertEqual("Start main loop\n", self.logger.output)
