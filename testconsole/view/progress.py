from urwid import (
    LEFT,
    ProgressBar,
)

from testtools.testresult.real import FINAL_STATES

from testconsole.testtools import EXISTS


class Progress(ProgressBar):
    """Render a progress bar with test case counters."""

    text_align = LEFT
    text_template = "total: {total} done: {done} left: {left} - {percentage}"

    def __init__(self, repository):
        super(Progress, self).__init__("progress normal", "progress complete")
        self._repository = repository
        self._bind()

    def get_text(self):
        return self.text_template.format(
            total=self._cases_total,
            done=self._cases_done,
            left=self._cases_left,
            percentage=super(Progress, self).get_text())

    def _bind(self):
        self._repository.on_counts_change += self._sync

    def _sync(self, repository):
        done = float(self._cases_done)
        total = float(self._cases_total)
        self.set_completion(int(done / total * 100))

    @property
    def _cases_total(self):
        return self._repository.count_records()

    @property
    def _cases_done(self):
        return self._repository.count_records(FINAL_STATES - {EXISTS})

    @property
    def _cases_left(self):
        return self._cases_total - self._cases_done
