from urwid import (
    WidgetWrap,
    Filler,
    Frame,
    Text,
    ExitMainLoop,
)

from testconsole.view import Header, Footer


class Console(WidgetWrap):
    """Top level widget handling the entire widget tree."""

    def __init__(self, repository, debug=False):
        """
        :param debug: If True, insert a pane where internal debugging messages
            will printed.
        """
        self._repository = repository
        self._header = Header(self._repository)
        self._body = Filler(Text(''), 'top')
        self._footer = Footer(self._repository, debug=debug)
        super(Console, self).__init__(Frame(
            header=self._header,
            body=self._body,
            footer=self._footer,
        ))

    def keypress(self, size, key):
        if key == "q":
            raise ExitMainLoop()
