from __future__ import absolute_import

from datetime import datetime
from logging import Formatter


class MillisecondFormatter(Formatter):
    """A formatter supporting also milliseconds."""

    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        created = self.converter(record.created)
        if datefmt:
            text = created.strftime(datefmt)
        else:
            text = created.strftime("%Y-%m-%d %H:%M:%S")
            text = "%s,%03d" % (text, record.msecs)
        return text
