import argparse
import logging
import sys

from workflower.cli.commands import FUNCTION_MAP

logger = logging.getLogger("workflower.cli.client")


class CLI:
    CLI_VERSION = "Workflower 0.0.1"

    def __init__(self):
        self.__run()

    def __run(self):
        self.parser = argparse.ArgumentParser(
            prog="workflower",
            description="Workflow automation tool.",
            epilog="Developed by Gabriel Menezes",
            usage="%(prog)s [options]",
        )

        self.parser.version = self.CLI_VERSION
        self.parser.add_argument(
            "-v",
            "--version",
            action="version",
        )

        self.parser.add_argument("command", choices=FUNCTION_MAP.keys())
        parser_args = self.parser.parse_args()
        if parser_args:
            try:
                command = parser_args.command
                if command:
                    func = FUNCTION_MAP[command]
                    func()
            except Exception as e:
                logger.error(f"Invalid argument: {e}")
                sys.exit(1)

        else:
            self.parser.print_help()
            sys.exit(1)
