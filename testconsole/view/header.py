from urwid import (
    WidgetWrap,
    Pile,
)

from testconsole.view import Progress
from testconsole.view import Record


class Header(WidgetWrap):

    def __init__(self, repository):
        super(Header, self).__init__(Pile([
            Progress(repository),
            Record(repository),
        ]))
