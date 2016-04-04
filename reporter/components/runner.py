"""This module provides the main functionality of codeclimate-test-reporter.

Invocation flow:

  1. Read, validate and process the input (args, `stdin`).
  2. Create and send test coverage to codeclimate.com.
  3. Report back to `stdout`.
  4. Exit.

"""
from coverage.misc import CoverageException
import os
import platform
import sys
import requests.exceptions

from ..__init__ import __version__ as reporter_version
from ..components.argument_parser import ArgumentParser
from ..components.payload_validator import InvalidPayload
from ..components.reporter import Reporter


class Runner:
    def run(self, args=sys.argv[1:], env=os.environ):
        """
        The main function.

        Pre-process args, handle some special types of invocations,
        and run the main program with error handling.

        Return exit status code.

        """

        try:
            parsed_args = ArgumentParser().parse_args(args)

            if parsed_args.debug:
                sys.stderr.write(self.__debug_info())
                return 0
            elif parsed_args.version:
                print(reporter_version)
                return 0
            else:
                reporter = Reporter(parsed_args)
                exit_status = reporter.run()
                return exit_status
        except CoverageException as e:
            return self.__handle_error(
                "Coverage file `" + parsed_args.file + "` file not found. "
                "Use --file <file> to specifiy an alternate location."
            )
        except InvalidPayload as e:
            return self.__handle_error("Invalid Payload: " + str(e), support=True)
        except requests.exceptions.HTTPError as e:
            return self.__handle_error(str(e), support=True)
        except requests.exceptions.Timeout:
            return self.__handle_error(
                "Client HTTP Timeout: No response in 5 seconds.",
                support=True
            )

    def __handle_error(self, message, support=False):
        sys.stderr.write(message)

        if support:
            sys.stderr.write(
                "\n\nContact support at https://codeclimate.com/help "
                "with the following debug info if error persists:"
                "\n" + message + "\n" + self.__debug_info()
            )

        return 1

    def __debug_info(self):
        from requests import __version__ as requests_version

        return "\n".join([
            "codeclimate-test-repoter %s" % reporter_version,
            "Requests %s" % requests_version,
            "Python %s\n%s" % (sys.version, sys.executable),
            "%s %s" % (platform.system(), platform.release()),
        ])
