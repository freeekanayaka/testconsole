import codecs
import errno

from subunit import ByteStreamToStreamResult
from subunit.v2 import (
    SIGNATURE,
    ParseError,
)


class AsyncByteStreamToStreamResult(ByteStreamToStreamResult):
    """Asynchronously read a subunit stream and relay to a test result."""

    def __init__(self, source):
        """
        :param source: A file-like object supporting non-blocking reads. Calls
            to ``source.read()`` should return immediately with available data,
            and raise OSError (EAGAIN) if more data is pending.
        """
        self.source = source
        self.codec = codecs.lookup('utf8').incrementaldecoder()

    def run(self, result):
        """Initialize the stream parser, don't ready any data just yet.

        This is a non-blocking call, it should be followed by calls to
        :meth:`do_read` when data is available for reading.
        """
        self.codec.reset()
        self._result = result

    def do_read(self):
        """Read and parse all available data on the source and emit events."""
        while True:
            try:
                content = self.source.read(1)
            except OSError as error:
                if error.errno == errno.EAGAIN:
                    return False
                raise
            if not content:
                return True
            if content[0] != SIGNATURE[0]:
                raise ParseError("Invalid packet signature")
            self._parse_packet(self._result)
