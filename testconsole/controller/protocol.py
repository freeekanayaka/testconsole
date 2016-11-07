from testconsole.urwid.protocol import AbstractProtocol
from testconsole.subunit import AsyncByteStreamToStreamResult


class SubunitProtocol(AbstractProtocol):
    """Glue between the urwid and subunit async abstractions."""

    def __init__(self, result):
        self._result = result

    def make_connection(self, transport):
        self._decoder = AsyncByteStreamToStreamResult(transport)
        self._decoder.run(self._result)

    def data_received(self):
        if self._decoder.do_read():
            self._done()
