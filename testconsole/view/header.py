from urwid import (
    WidgetWrap,
    Pile,
)

from testconsole.view import Progress
from testconsole.view import CaseView


class Header(WidgetWrap):

    def __init__(self, repository):
        super(Header, self).__init__(Pile([
            Progress(repository),
            CaseView(repository),
        ]))
