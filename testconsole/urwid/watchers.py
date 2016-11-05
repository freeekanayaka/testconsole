"""Watchers for various byte stream data sources.

Watchers can be attached to Urwid's stock main loop, and will be notified when
data is available for reading on their underlying byte stream. At that point
they will in turn notify the protocol object that they are passed in the
``attach`` method.

They provide a unified abstraction for different types of data sources (from
file, process, etc) and are somehow similar to Twisted's IReadDescriptor.
"""
import os
import logging
import signal
import subprocess

from testconsole.python.io import AsyncBytesIO
from testconsole.urwid.protocol import ProtocolDone


class AbstractWatcher(object):
    """Abstract watcher providing implementation of common interfaces."""

    def __init__(self):
        self._transport = None
        self._loop = None

    def attach(self, loop, protocol):
        """Attach this watcher to the given main loop.

        This will trigger ``make_connection`` in the given protocol.

        :param protocol: An object implementing the protocol interface (see
            :class:``AbstractProtocol``).
        """
        self._protocol = protocol
        self._loop = loop
        self._transport = self._start_watching()
        self._protocol.make_connection(self._transport)

    def detach(self):
        """Detach this watcher from its loop."""
        logging.debug("Detach watcher")
        self._stop_watching()

    def _start_watching(self):
        """Must be implemented by sub-classes."""

    def _stop_watching(self):
        """Must be implemented by sub-classes."""

    def _data_received(self):
        try:
            self._protocol.data_received()
        except ProtocolDone:
            logging.debug("Protocol requested to close the connection")
            self.detach()


class FileWatcher(AbstractWatcher):
    """Watch a file-like stream (could be a FIFO as well)."""

    def __init__(self, filename):
        """
        :param filename: The path to the file to read from.
        """
        super(FileWatcher, self).__init__()
        self._filename = filename
        self._handle = None

    def _start_watching(self):
        logging.debug("Attach file stream watcher for %s", self._filename)

        fd = os.open(self._filename, os.O_RDONLY | os.O_NONBLOCK)
        self._handle = self._loop.watch_file(fd, self._data_received)
        return os.fdopen(fd, "rb")

    def _stop_watching(self):
        self._loop.remove_watch_file(self._handle)
        self._transport.close()


class ProcessWatcher(AbstractWatcher):
    """Watch the standard output stream of a process."""

    def __init__(self, command):
        """
        :param command: The command to use to spawn the process.
        """
        super(ProcessWatcher, self).__init__()
        self._command = command
        self._process = None
        self._pipe = None

    def _start_watching(self):
        logging.debug("Watch stream from command %s", self._command)

        # Since Urwid unconditionally perform the read for us, we have to
        # replicate it on our AsyncBytesIO.
        self._transport = AsyncBytesIO()

        signal.signal(signal.SIGCHLD, self._process_exited)
        self._pipe = self._loop.watch_pipe(self._process_data_received)
        self._process = subprocess.Popen(
            self._command, stdout=self._pipe, close_fds=True)

        return self._transport

    def _process_data_received(self, data):
        self._transport.seek(0)
        self._transport.truncate()
        self._transport.write(data)
        self._transport.seek(0)
        self._data_received()

    def _process_exited(self, signal, info):
        # This is a race between SIGCHLD and Popen and can't be really
        # unit tested.
        if self._process is not None:  # pragma: no cover
            returncode = self._process.poll()
            logging.debug("Command exited with %d", returncode)

        self._transport.eof = True
        self._loop.set_alarm_in(0, lambda *a, **k: self._data_received())

    def _stop_watching(self):
        self._loop.remove_watch_pipe(self._pipe)
        self._transport.close()


class MemoryWatcher(AbstractWatcher):
    """Watch an in-memory BytesIO stream."""

    def __init__(self, stream):
        """
        :param filename: The path to the file to read from.
        """
        super(MemoryWatcher, self).__init__()
        self._stream = stream

    def attach(self, loop, protocol):
        logging.debug("Attach memory stream watcher")
        self._stream.seek(0)
        self._protocol = protocol
        self._protocol.make_connection(self._stream)
        # Fire the data received callback synchronously. Since this
        # watcher is meant for testing, it's safe to assume that the
        # data is already available.
        self._data_received()
