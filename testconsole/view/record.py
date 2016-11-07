from logging import (
    ERROR,
    LogRecord,
)

from urwid import (
    WidgetWrap,
    LineBox,
    Text,
)

from testconsole import defaultFormatter


class Record(WidgetWrap):
    """Render details about a single test case."""

    def __init__(self, repository):
        self._repository = repository
        self._log = Text("")
        self._box = LineBox(self._log)
        self._bind()
        super(Record, self).__init__(self._box)

    def _bind(self):
        self._repository.on_record_start += self._update_title
        self._repository.on_record_progress += self._update_logs

    def _update_title(self, repository, record):
        self._box.set_title(record.id)
        self._log.set_text("")

    def _update_logs(self, repository, record):

        log = ""
        traceback = ""

        for name, detail in record.details.items():
            text = detail.as_text().strip()
            if detail.content_type.subtype == "x-log":
                log += text
            elif detail.content_type.subtype == "x-traceback":
                # XXX Figure out how to get the timestamp from the original
                #     subunit packet, instead of letting LogRecord create
                #     a local timestamp.
                log_record = LogRecord(
                    name, ERROR, None, None, text, None, None)
                traceback += defaultFormatter.format(log_record)

        self._log.set_text(log + traceback)
