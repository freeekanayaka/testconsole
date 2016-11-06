from testtools import TestCase
from fixtures import FakeLogger

from testconsole.model import Repository


class ViewTest(TestCase):

    def setUp(self):
        super(ViewTest, self).setUp()
        self.logger = self.useFixture(FakeLogger())
        self.repository = Repository()
