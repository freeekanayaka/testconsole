from testconsole.python import Undef


class Case(object):
    """Hold information about a single test case."""

    def __init__(self, test_id):
        self.id = test_id
        self.state = Undef
