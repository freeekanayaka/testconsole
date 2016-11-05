from urwid import Text

from testconsole.python import MillisecondFormatter


class Logger(Text):
    """Render a message stream using a stdlib logging formatter.

    It can be used standalone, or has a backend for a ``logging.Handler``
    registered in the stdlib logging system.
    """

    _formatter = MillisecondFormatter(
        fmt="%(asctime)s [%(name)s:%(levelname)s] %(message)s",
        datefmt="%H:%M:%S,%f",
    )

    def __init__(self, max_records=None):
        """
        :param max_records: If not ``None``, only render up to this amount of
            records.
        """
        super(Logger, self).__init__("")
        self.max_records = max_records

    def emit(self, record):
        lines = self.text.split("\n") + [self._formatter.format(record)]
        if lines[0] == "":
            lines.pop(0)
        if self.max_records and len(lines) > self.max_records:
            lines[:] = lines[-self.max_records:len(lines)]
        self.set_text("\n".join(lines))
