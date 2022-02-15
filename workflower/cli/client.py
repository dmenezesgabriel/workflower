import argparse
import logging
import os
import sys

from workflower.cli.commands import FUNCTION_MAP
from workflower.config import Config

logger = logging.getLogger("workflower.cli.client")


def _load_splash():
    splash_path = os.path.join(
        Config.BASE_DIR, "workflower", "resources", "splash.txt"
    )
    with open(splash_path, "r") as f:
        splash = f.read()
    return splash


def _show_splash():
    splash = _load_splash()
    clear_console = "clear" if os.name == "posix" else "CLS"
    os.system(clear_console)
    sys.stdout.write(splash)
    sys.stdout.write("\n")


def _get_command(command, *args, **kwagrs):
    func = FUNCTION_MAP[command]
    func(*args)


class CLI:
    """
    Workflower Command Line Interface.
    """

    CLI_VERSION = "Workflower 0.0.1"

    def __init__(self):
        self.__run()

    def __run(self):
        """
        Setup and parse command line arguments and options.
        """

        _show_splash()
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
        self.parser.add_argument(
            "-i", "--input", dest="filename", required=False
        )
        parser_args = self.parser.parse_args()
        if parser_args:
            print(parser_args)
            try:
                command = parser_args.command
                if command:
                    if parser_args.filename:
                        path = parser_args.filename
                        _get_command(command, path)
                    else:
                        _get_command(command)

            except Exception as e:
                logger.error(f"Invalid argument: {e}")
                sys.exit(1)

        else:
            self.parser.print_help()
            sys.exit(1)
