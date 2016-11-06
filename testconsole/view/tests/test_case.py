from six import b

from testtools.matchers import (
    Contains,
    Not,
)

from testconsole.model import (
    INPROGRESS,
    SUCCESS,
)
from testconsole.view import (
    ViewTest,
    CaseView,
)


class ProgressTest(ViewTest):

    def setUp(self):
        super(ProgressTest, self).setUp()
        self.case = CaseView(self.repository)

    def test_render_status_inprogress(self):
        """
        When a test moves to the INPROGRESS, the box title gets updated.
        """
        self.repository.add_case("foo")
        self.repository.set_state("foo", INPROGRESS)
        canvas = self.case.render((50,))
        self.assertThat(canvas.text[0], Contains(b("foo")))

    def test_render_status_success(self):
        """
        When a test moves to a state that is not INPROGRESS, the box title
        stays the same.
        """
        self.repository.add_case("foo")
        self.repository.set_state("foo", SUCCESS)
        canvas = self.case.render((50,))
        self.assertThat(canvas.text[0], Not(Contains(b("foo"))))
