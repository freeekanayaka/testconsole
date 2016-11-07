from urwid import (
    WidgetWrap,
    LineBox,
    Text,
)


class Record(WidgetWrap):
    """Render details about a single test case."""

    def __init__(self, repository):
        self._repository = repository
        self._text = Text("")
        self._box = LineBox(self._text)
        self._bind()
        super(Record, self).__init__(self._box)

    def _bind(self):
        self._repository.on_change_inprogress_record += self._update_title

    def _update_title(self, repository, record):
        self._box.set_title(record.id)
