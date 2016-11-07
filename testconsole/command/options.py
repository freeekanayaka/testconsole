from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace


class Options(Namespace):
    """Available testconsole options."""

    def __init__(self):
        super(Namespace, self).__init__()
        self._parser = self._build_parser()
        self.update(())

    def update(self, args):
        """Update the options by parsing the given command line arguments."""

        extras = []
        if "--" in args:
            pivot = args.index("--")
            extras.extend(args[pivot + 1:])
            args = args[:pivot]

        self._parser.parse_args(args=args, namespace=self)

        if self.command:
            self.command = [self.command] + extras

    def _build_parser(self):
        """Create the argument parser."""
        parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

        self._add_global_arguments(parser)

        return parser

    def _add_global_arguments(self, parser):
        """Add global arguments."""
        source = parser.add_mutually_exclusive_group()
        source.add_argument(
            "-f", "--file", dest="filename", metavar="PATH",
            help="Read the subunit stream from this file (it can also be"
                 "a special file, like a FIFO"),
        source.add_argument(
            "-c", "--command", metavar="COMMAND",
            help="Spawn this command read the subunit stream from its stdout")
        parser.add_argument(
            "-d", "--debug", action="store_true",
            help="Print internal debugging information in a special UI frame")
