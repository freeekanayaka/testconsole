import sys
import logging

from urwid import MainLoop

from testconsole.urwid import (
    FileWatcher,
    ProcessWatcher,
)
from testconsole.command import Options
from testconsole.view import (
    PALETTE,
    Console,
)
from testconsole.model import Repository
from testconsole.controller import Controller


def main(argv=None, loop_factory=MainLoop):

    if argv is None:  # pragma: no cover
        argv = sys.argv

    options = Options()
    options.update(argv[1:])

    if options.filename:
        watcher = FileWatcher(options.filename)
    else:
        watcher = ProcessWatcher(options.command)

    repository = Repository()

    console = Console(repository, debug=options.debug)
    loop = loop_factory(console, palette=PALETTE)

    controller = Controller(watcher, repository)
    controller.attach(loop)

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Start main loop")

    loop.run()


if __name__ == "__main__":  # pragma: no cover
    main()
