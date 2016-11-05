from six import (
    BytesIO,
    b,
)

from testtools import TestCase
from fixtures import TempDir

from urwid import (
    MainLoop,
    ExitMainLoop,
)

from testconsole.urwid import (
    FileWatcher,
    ProcessWatcher,
    MemoryWatcher
)
from testconsole.urwid import AbstractProtocol


class DummyProtocol(AbstractProtocol):

    def __init__(self, loop):
        self.loop = loop
        self.reads = []

    def make_connection(self, transport):
        self.transport = transport

    def data_received(self):
        data = self.transport.read(4096)
        self.reads.append(data)
        if data == b(""):
            self.loop.set_alarm_in(0, self._exit_loop)
            self._done()

    def _exit_loop(self, *args, **kwargs):
        raise ExitMainLoop()


class FileWatcherTest(TestCase):

    def setUp(self):
        super(FileWatcherTest, self).setUp()
        self.filename = self.useFixture(TempDir()).join("foo")
        with open(self.filename, "wb") as fd:
            fd.write(b("hello"))
        self.loop = MainLoop(None)
        self.protocol = DummyProtocol(self.loop)
        self.watcher = FileWatcher(self.filename)

    def test_attach(self):
        """
        When data is available for reading, the protocol gets notified.
        """
        self.watcher.attach(self.loop, self.protocol)
        self.loop.event_loop.run()
        self.assertTrue(self.protocol.transport.closed)
        self.assertEqual([b("hello"), b("")], self.protocol.reads)

    def test_detached(self):
        """
        When the watcher is detached from the loop, the underlying file
        descriptor gets closed.
        """
        self.watcher.attach(self.loop, self.protocol)
        self.watcher.detach()
        self.assertTrue(self.protocol.transport.closed)


class ProcessWatcherTest(TestCase):

    def setUp(self):
        super(ProcessWatcherTest, self).setUp()
        self.loop = MainLoop(None)
        self.protocol = DummyProtocol(self.loop)
        self.watcher = ProcessWatcher(["uptime"])

    def test_attach(self):
        """
        When data is available for reading, the given protocol gets notified.
        """
        self.watcher.attach(self.loop, self.protocol)

        # Wait for the process to complete, so the loop will have something
        # to ready when we kick it off.
        self.watcher._process.wait()

        self.loop.event_loop.run()
        self.assertTrue(self.protocol.transport.closed)

        # We expect 2 reads, one with the output of the command and a second
        # one that get kicked when the process terminates, and should act
        # as EOF signal.
        read1, read2 = self.protocol.reads
        self.assertIn(b("load average"), read1)
        self.assertEqual(b(""), read2)

    def test_detach(self):
        """
        When the watcher is removed from the loop, the underlying file
        descriptor gets closed.
        """
        self.watcher.attach(self.loop, self.protocol)

        # Wait for the process to complete, so we don't leave garbage around.
        self.watcher._process.wait()

        self.watcher.detach()
        self.assertTrue(self.protocol.transport.closed)


class MemoryWatcherTest(TestCase):

    def setUp(self):
        super(MemoryWatcherTest, self).setUp()
        self.stream = BytesIO()
        self.loop = MainLoop(None)
        self.protocol = DummyProtocol(self.loop)
        self.watcher = MemoryWatcher(self.stream)

    def test_attach(self):
        """
        When data is available for reading, the protocol gets notified.
        """
        self.stream.write(b("hello"))
        self.watcher.attach(self.loop, self.protocol)
        self.assertEqual([b("hello")], self.protocol.reads)
