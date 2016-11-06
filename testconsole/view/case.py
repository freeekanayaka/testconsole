from urwid import (
    WidgetWrap,
    LineBox,
    Text,
)


class CaseView(WidgetWrap):
    """Render details about a single test case."""

    def __init__(self, repository):
        self._repository = repository
        self._text = Text("")
        self._box = LineBox(self._text)
        self._bind()
        super(CaseView, self).__init__(self._box)

    def _bind(self):
        self._repository.set_state += self._update_title

    def _update_title(self, repository, test_id, test_status):
        if test_status == "inprogress":
            self._box.set_title(test_id)
