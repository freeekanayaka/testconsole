from logging import (
    getLogger,
    Handler,
)

from urwid import WidgetWrap
from testconsole.urwid import Logger


class Footer(WidgetWrap):
    """Render a footer displaying local logging."""

    def __init__(self, repository, debug=False):
        self._repository = repository
        max_records = None if debug else 1
        self._messages = Logger(max_records=max_records)
        self._bind()
        super(Footer, self).__init__(self._messages)

    def _bind(self):
        root = getLogger()
        handler = Handler()
        handler.emit = self._messages.emit
        root.addHandler(handler)
