from testtools import TestCase

from testconsole.command import Options


class OptionsTestCase(TestCase):

    def setUp(self):
        super(OptionsTestCase, self).setUp()
        self.options = Options()

    def test_extras(self):
        """It's possible to pass extra options for the test command."""
        self.options.update(["-c", "python", "--", "-m", "foo"])
        self.assertEqual(["python", "-m", "foo"], self.options.command)
