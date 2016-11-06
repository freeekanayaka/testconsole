import logging

from six import b

from testtools.matchers import Contains

from testconsole.view import (
    ViewTest,
    Footer,
)


class FooterTest(ViewTest):

    def test_render(self):
        """
        The console creates a pile of panes widgets.
        """
        footer = Footer(self.repository)
        logging.critical("Achtung!")
        canvas = footer.render((10,))
        self.assertThat(b("").join(canvas.text), Contains(b("Achtung!")))
