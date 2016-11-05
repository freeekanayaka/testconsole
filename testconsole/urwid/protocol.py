"""Lightweight protocol abstraction for Urwid's stock main loop.

Loosely designed against Twisted/asyncio.
"""


class AbstractProtocol(object):

    def make_connection(self, transport):
        """Connect the protocol to a transport.

        :param transport: A file-like object supporting non-blocking reads.
        """

    def data_received(self):
        """Notification that the transport has data available for reading.

        :raises: :class:``ProtocolDone`` when the protocol wants to terminate
            the connection.
        """

    def _done(self):
        """Convenience for raising :class:``ProtocolDone``."""
        raise ProtocolDone()


class ProtocolDone(Exception):
    """
    Raised by concrete ``AbstractProtocol.data_received`` implementations
    that want to terminate the connection.
    """
