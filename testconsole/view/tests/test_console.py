from urwid import (
    Frame,
    ExitMainLoop,
)

from testconsole.view import (
    ViewTest,
    Console,
    Header,
    Footer,
)


class ConsoleTest(ViewTest):

    def setUp(self):
        super(ConsoleTest, self).setUp()
        self.console = Console(self.repository)

    def test_render(self):
        """
        The console creates a frame with header and footer.
        """
        canvas = self.console.render((10, 10))
        frame = canvas.children[0][2].widget_info[0]
        self.assertIsInstance(frame, Frame)
        self.assertIsInstance(frame.get_header(), Header)
        self.assertIsInstance(frame.get_footer(), Footer)

    def test_keypress_q(self):
        """
        If the key 'q' is pressed, the loop exists.
        """
        self.assertRaises(ExitMainLoop, self.console.keypress, 1, "q")
