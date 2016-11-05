import os
import errno

from cStringIO import StringIO


class AsyncStringIO(object):
    """A StringIO variant that mimics a file object in non-blocking mode."""

    def __init__(self):
        self.eof = False
        self.buffer = StringIO()

    def read(self, length):
        """Read up to the given amount of bytes.

        If the ``eof`` instance attribute is set to ``False``, then
        an ``OSError`` will be raised if there aren't any more bytes
        available to read.
        """
        data = self.buffer.read(length)
        if data == "" and not self.eof:
            error = OSError(errno.EAGAIN, os.strerror(errno.EAGAIN))
            raise error
        return data

    def __getattr__(self, name):
        return getattr(self.buffer, name)
